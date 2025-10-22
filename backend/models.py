from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import BYTEA
from database import Base

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)

    # Personal / contact
    first_name = Column(String(80), nullable=False)
    last_name  = Column(String(80), nullable=False)
    address    = Column(String(300), nullable=True)
    city       = Column(String(120), nullable=True)
    state      = Column(String(2), nullable=True)
    zip        = Column(String(20), nullable=True)
    home_phone = Column(String(40), nullable=True)
    cell_phone = Column(String(40), nullable=True)
    email      = Column(String(255), nullable=True)

    # Experience / flags
    is_agent   = Column(Boolean, nullable=False, default=False)
    years_exp  = Column(Integer, nullable=True)

    # Sensitive
    ssn_encrypted = Column(BYTEA, nullable=False)
    ssn_last4     = Column(String(4), nullable=False)

    # Attachments / consent
    resume_path       = Column(String(500), nullable=True)
    background_consent = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
