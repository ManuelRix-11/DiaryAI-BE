from pydantic import BaseModel, EmailStr


# Definizione dei modelli di richiesta/risposta
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: str = None
    email: EmailStr = None
    password: str = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr

class UserLogRequest(BaseModel):
    email: EmailStr
    password: str
