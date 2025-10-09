from __future__ import annotations
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

router = APIRouter()
_user_db: Dict[str, Dict[str, object]] = {}
_seq = 0

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class RegisterOut(BaseModel):
    message: str
    client_id: int

@router.post("/register", response_model=RegisterOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn):
    global _seq
    if data.email in _user_db:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    _seq += 1
    _user_db[data.email] = {"id": _seq, "password": data.password}
    return RegisterOut(message="registered", client_id=_seq)
