from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel

from app.services import diary_service


# Definizione dei modelli di richiesta/risposta
class DiaryCreate(BaseModel):
    title: str
    user_id: str


class DiaryUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None


class DiaryResponse(BaseModel):
    id: str
    title: str
    text: str
    created_at: str
    updated_at: str
    sentiment: Optional[Dict[str, Any]] = None


class SentimentResponse(BaseModel):
    sentiment: str
    score: float
    sentiments: List[Dict[str, Any]]


# Router
diary_router = APIRouter(prefix="/diaries", tags=["Diari"])


@diary_router.get("/", response_model=List[DiaryResponse])
async def list_entries():
    """
    Recupera tutti i diari dal sistema.
    """
    try:
        diaries = await diary_service.get_all_diary_entries()
        return [{
            "id": str(diary.id),
            "title": diary.title,
            "text": diary.text,
            "created_at": diary.created_at.isoformat(),
            "updated_at": diary.updated_at.isoformat(),
            "sentiment": diary.sentiment
        } for diary in diaries]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nel recupero dei diari: {str(e)}"
        )


@diary_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Dict[str, str])
async def create_entry(diary_data: DiaryCreate):
    """
    Crea un nuovo diario per l'utente specificato.
    """
    try:
        result = await diary_service.create_diary_entry(
            user_id=diary_data.user_id,
            title=diary_data.title
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nella creazione del diario: {str(e)}"
        )


@diary_router.get("/{entry_id}", response_model=DiaryResponse)
async def get_entry(entry_id: str):
    """
    Recupera un diario specifico tramite il suo ID.
    """
    diary = await diary_service.get_diary_by_id(entry_id)
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diario non trovato"
        )

    return {
        "id": str(diary.id),
        "title": diary.title,
        "text": diary.text,
        "created_at": diary.created_at.isoformat(),
        "updated_at": diary.updated_at.isoformat(),
        "sentiment": diary.sentiment
    }


@diary_router.put("/{entry_id}", response_model=DiaryResponse)
async def update_entry(entry_id: str, diary_data: DiaryUpdate):
    """
    Aggiorna un diario esistente.
    Se il testo viene modificato, viene eseguita automaticamente l'analisi del sentiment.
    """
    # Converti il modello Pydantic in dizionario, escludendo i campi non impostati
    update_data = diary_data.dict(exclude_unset=True)

    # Aggiorna il diario
    diary = await diary_service.update_diary_entry(entry_id, update_data)
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diario non trovato"
        )

    return {
        "id": str(diary.id),
        "title": diary.title,
        "text": diary.text,
        "created_at": diary.created_at.isoformat(),
        "updated_at": diary.updated_at.isoformat(),
        "sentiment": diary.sentiment
    }


@diary_router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(entry_id: str):
    """
    Elimina un diario specifico.
    """
    deleted = await diary_service.delete_diary_entry(entry_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diario non trovato"
        )
    return None


@diary_router.get("/user/{user_id}", response_model=List[DiaryResponse])
async def get_user_diaries(user_id: str):
    """
    Recupera tutti i diari appartenenti a un utente specifico.
    """
    diaries = await diary_service.get_diaries_by_user(user_id)
    return [{
        "id": str(diary.id),
        "title": diary.title,
        "text": diary.text,
        "created_at": diary.created_at.isoformat(),
        "updated_at": diary.updated_at.isoformat(),
        "sentiment": diary.sentiment
    } for diary in diaries]


@diary_router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(text: str = Query(..., description="Testo da analizzare")):
    """
    Analizza il sentiment di un testo fornito.
    """
    try:
        result = await diary_service.sentiment_analysis(None, text)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nell'analisi del sentiment: {str(e)}"
        )