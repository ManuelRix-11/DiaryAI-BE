from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr

from app.schema.user_schema import UserResponse, UserCreate, UserUpdate, UserLogRequest
from app.services import user_service

# Router
user_router = APIRouter(prefix="/users", tags=["Utenti"])


@user_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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

@user_router.post("/login", response_model=UserResponse)
async def login(log_user: UserLogRequest):
    user = await user_service.authenticate_user(log_user.email, log_user.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenziali non valide")
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email
    }

@user_router.get("/{user_id}/stats", response_model=List[float])
async def get_stats_by_user(user_id: str):
    """
    Restituisce le statistiche di un utente:
    [numero_di_diari, streak_giorni_consecutivi, mood]
    """
    stats = await user_service.get_user_stats(user_id)
    if stats == [0, 0, 0.0]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    return stats