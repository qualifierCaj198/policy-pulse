import os, shutil, uuid
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import Submission, AdminUser
from security import encrypt_ssn, mask_last4
from auth import router as auth_router, get_current_admin

app = FastAPI(title="Policy Pulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# Health
@app.get("/healthz")
def health():
    return {"ok": True}

# Public intake: multipart/form-data
@app.post("/submit")
def submit_payload(
    first_name: str = Form(...),
    last_name: str = Form(...),
    address: str | None = Form(None),
    city: str | None = Form(None),
    state: str | None = Form(None),
    zip: str | None = Form(None),
    home_phone: str | None = Form(None),
    cell_phone: str | None = Form(None),
    email: str | None = Form(None),
    is_agent: bool = Form(...),
    years_exp: int | None = Form(None),
    ssn: str = Form(...),
    background_consent: bool = Form(...),
    resume: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    if not background_consent:
        raise HTTPException(status_code=400, detail="Background consent is required")
    # store core data
    s = Submission(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        address=(address or None),
        city=(city or None),
        state=(state or None),
        zip=(zip or None),
        home_phone=(home_phone or None),
        cell_phone=(cell_phone or None),
        email=(email or None),
        is_agent=bool(is_agent),
        years_exp=years_exp,
        ssn_encrypted=encrypt_ssn(ssn.strip()),
        ssn_last4=mask_last4(ssn),
        background_consent=True,
    )
    db.add(s)
    db.commit()
    db.refresh(s)

    # handle resume upload
    if resume and resume.filename:
        uploads_dir = "/app/uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        # safe filename
        ext = os.path.splitext(resume.filename)[1]
        filename = f"{s.id}_{uuid.uuid4().hex}{ext}"
        full_path = os.path.join(uploads_dir, filename)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(resume.file, f)
        s.resume_path = f"/files/{filename}"
        db.add(s)
        db.commit()

    return {"ok": True, "id": s.id}

# Protected listing for admin (returns FULL SSN)
@app.get("/admin/submissions")
def list_submissions(admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    rows = db.query(Submission).order_by(Submission.id.desc()).limit(500).all()
    out = []
    from security import FERNET
    for r in rows:
        ssn_full = FERNET.decrypt(bytes(r.ssn_encrypted)).decode()
        out.append({
            "id": r.id,
            "first_name": r.first_name,
            "last_name": r.last_name,
            "address": r.address,
            "city": r.city,
            "state": r.state,
            "zip": r.zip,
            "home_phone": r.home_phone,
            "cell_phone": r.cell_phone,
            "email": r.email,
            "is_agent": r.is_agent,
            "years_exp": r.years_exp,
            "ssn": ssn_full,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "resume_path": r.resume_path,
            "background_consent": r.background_consent,
        })
    return out

# Serve uploaded files (nginx will usually serve; this is a fallback if proxied)
from fastapi.responses import FileResponse, Response
from fastapi import Request
import mimetypes

@app.get("/files/{name}")
def get_file(name: str):
    path = os.path.join("/app/uploads", name)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Not found")
    mime, _ = mimetypes.guess_type(path)
    return FileResponse(path, media_type=mime or "application/octet-stream")

# Mount auth routes
app.include_router(auth_router)
