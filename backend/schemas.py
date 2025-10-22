from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

class AdminLoginIn(BaseModel):
    email: EmailStr
    password: str

class AdminToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
