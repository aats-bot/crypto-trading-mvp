from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from src.api.services.client_service import ClientService

router = APIRouter()

class RegisterPayload(BaseModel):
    email: EmailStr
    password: str
    bybit_api_key: str
    bybit_api_secret: str

class LoginPayload(BaseModel):
    username: EmailStr
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterPayload):
    svc = ClientService()
    try:
        client = svc.create_client(
            email=payload.email,
            password=payload.password,
            bybit_api_key=payload.bybit_api_key,
            bybit_api_secret=payload.bybit_api_secret,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "registered", "client_id": getattr(client, "id", None)}

@router.post("/login")
def login(payload: LoginPayload):
    svc = ClientService()
    result = svc.authenticate_client(username=payload.username, password=payload.password)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    # Os testes não exigem formato específico além de 200 – mas vamos devolver algo útil:
    return {
        "client_id": result.get("client_id"),
        "token": result.get("token"),
        "expires_in": result.get("expires_in"),
    }
