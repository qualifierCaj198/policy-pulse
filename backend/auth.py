import os, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database import get_db
from models import AdminUser
from security import verify_password, hash_password

router = APIRouter(prefix="/admin", tags=["admin-auth"])

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_EXPIRE_MIN = int(os.getenv("JWT_EXPIRE_MIN", "43200"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

def create_token(sub: str) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + datetime.timedelta(minutes=JWT_EXPIRE_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> AdminUser:
    cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        sub = payload.get("sub")
        if not sub:
            raise cred_exc
    except JWTError:
        raise cred_exc
    admin = db.query(AdminUser).filter_by(email=sub, is_active=True).first()
    if not admin:
        raise cred_exc
    return admin

@router.post("/bootstrap")
def bootstrap_admin(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    exists = db.query(AdminUser).filter(AdminUser.email == email.lower()).first()
    if exists:
        return {"ok": True}  # idempotent
    u = AdminUser(email=email.lower(), password_hash=hash_password(password))
    db.add(u)
    db.commit()
    return {"ok": True}

@router.post("/login")
def admin_login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.email == email.lower()).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": create_token(user.email), "token_type": "bearer"}
