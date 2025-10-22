import os, re
from cryptography.fernet import Fernet
from passlib.context import CryptContext

FERNET = Fernet(os.environ["FERNET_KEY"])
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

SSN_RE = re.compile(r"^\d{3}-?\d{2}-?\d{4}$")

def mask_last4(ssn: str) -> str:
    d = re.sub(r"\D", "", ssn)
    return d[-4:]

def encrypt_ssn(ssn: str) -> bytes:
    return FERNET.encrypt(ssn.encode())

def verify_password(plain, hashed) -> bool:
    return pwd_ctx.verify(plain, hashed)

def hash_password(plain) -> str:
    return pwd_ctx.hash(plain[:72])
