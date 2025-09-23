from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.models.user import User
from app.services import user_service


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


# Router
user_router = APIRouter(prefix="/users", tags=["Utenti"])


@user_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """
    Crea un nuovo utente nel sistema.
    Verifica che l'email non sia già registrata.
    """
    existing = await user_service.get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email già registrata"
        )

    user = await user_service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )

    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email
    }


@user_router.get("/", response_model=List[UserResponse])
async def list_users():
    """
    Recupera l'elenco di tutti gli utenti registrati.
    """
    try:
        users = await user_service.list_users()
        return [{
            "id": str(user.id),
            "username": user.username,
            "email": user.email
        } for user in users]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nel recupero degli utenti: {str(e)}"
        )


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """
    Recupera un utente specifico tramite il suo ID.
    """
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )

    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email
    }


@user_router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate):
    """
    Aggiorna i dati di un utente esistente.
    """
    # Converti il modello Pydantic in dizionario, escludendo i campi non impostati
    update_data = user_data.dict(exclude_unset=True)

    # Aggiorna l'utente
    user = await user_service.update_user(user_id, update_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )

    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email
    }


@user_router.delete("/{user_id}", response_model=Dict[str, str])
async def delete_user(user_id: str):
    """
    Elimina un utente dal sistema.
    """
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )

    return {"message": "Utente eliminato correttamente"}


@user_router.get("/search/{search_term}", response_model=List[UserResponse])
async def search_users(search_term: str):
    """
    Cerca utenti per username o email.
    """
    users = await user_service.search_users(search_term)
    return [{
        "id": str(user.id),
        "username": user.username,
        "email": user.email
    } for user in users]