from datetime import datetime
from typing import List, Dict, Optional, Union
from beanie.operators import In

from app.models.diary import Diary
from app.models.user import User
from transformers import pipeline, AutoTokenizer

# Inizializzazione del tokenizer e del modello di sentiment analysis
tokenizer = AutoTokenizer.from_pretrained("MilaNLProc/feel-it-italian-emotion")
emotion_pipeline = pipeline(
    "text-classification",
    model="MilaNLProc/feel-it-italian-emotion",
    top_k=None
)


async def create_diary_entry(user_id: str, title: str) -> Dict[str, str]:
    """
    Crea un nuovo diario per l'utente specificato.

    Args:
        user_id: L'ID dell'utente proprietario del diario
        title: Il titolo del diario

    Returns:
        Dizionario contenente l'ID e il titolo del diario creato
    """
    user = await User.get(user_id)
    diary = Diary(
        title=title,
        text="",
        user=user,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        sentiment=None
    )
    await diary.insert()
    return {"id": str(diary.id), "title": diary.title}


async def get_all_diary_entries() -> List[Diary]:
    """
    Recupera tutti i diari dal database.

    Returns:
        Lista di tutti i documenti Diary
    """
    return await Diary.find_all().to_list()


async def get_diary_by_id(entry_id: str) -> Optional[Diary]:
    """
    Recupera un diario specifico tramite ID.

    Args:
        entry_id: L'ID del diario da recuperare

    Returns:
        Il documento Diary o None se non trovato
    """
    return await Diary.get(entry_id)


async def get_diaries_by_user(user_id: str) -> List[Diary]:
    """
    Recupera tutti i diari di un utente specifico.

    Args:
        user_id: L'ID dell'utente proprietario

    Returns:
        Lista dei diari dell'utente
    """
    user = await User.get(user_id)
    return await Diary.find({"user.id": user.id}).to_list()


async def update_diary_entry(entry_id: str, entry_data: Dict) -> Optional[Diary]:
    """
    Aggiorna un diario esistente con nuove informazioni e analisi del sentiment.

    Args:
        entry_id: L'ID del diario da aggiornare
        entry_data: Dizionario con i dati da aggiornare

    Returns:
        Il documento Diary aggiornato o None se non trovato
    """
    diary = await Diary.get(entry_id)
    if not diary:
        return None

    # Estrai il testo e analizza il sentiment se presente
    text = entry_data.get("text", diary.text)
    sentiment_result = None
    if text and text != diary.text:
        sentiment_result = await sentiment_analysis(None, text)

    # Aggiorna i campi del diario
    if "title" in entry_data:
        diary.title = entry_data["title"]
    if "text" in entry_data:
        diary.text = entry_data["text"]
    diary.updated_at = datetime.utcnow()
    if sentiment_result:
        diary.sentiment = sentiment_result

    await diary.save()
    return diary


async def delete_diary_entry(entry_id: str) -> bool:
    """
    Elimina un diario specificato dal database.

    Args:
        entry_id: L'ID del diario da eliminare

    Returns:
        True se l'eliminazione ha avuto successo, False altrimenti
    """
    try:
        diary = await Diary.get(entry_id)
        if not diary:
            return False
        await diary.delete()
        return True
    except Exception as e:
        print(f"Errore durante l'eliminazione del diario: {str(e)}")
        return False


async def sentiment_analysis(user: Optional[User], text: str) -> Dict:
    """
    Analizza il sentiment di un testo, supportando testi più lunghi dividendoli in chunk.

    Args:
        user: Utente (opzionale)
        text: Testo da analizzare

    Returns:
        Dizionario con i risultati dell'analisi del sentiment
    """
    tokens = tokenizer.encode(text)

    # Per testi brevi, analizza direttamente
    if len(tokens) <= 512:
        result = emotion_pipeline(text)
        sentiments = result[0]
        best = max(sentiments, key=lambda x: x['score'])
        return {
            "sentiment": best['label'],
            "score": best['score'],
            "sentiments": sentiments
        }

    # Per testi lunghi, dividi in chunk e analizza separatamente
    max_length = 450
    stride = 300

    chunks = []
    for i in range(0, len(tokens), stride):
        chunk = tokens[i:i + max_length]
        chunk_text = tokenizer.decode(chunk, skip_special_tokens=True)
        chunks.append(chunk_text)

    # Analizza ciascun chunk
    all_results = []
    for chunk in chunks:
        result = emotion_pipeline(chunk)
        all_results.append(result[0])

    # Combina i risultati - media dei punteggi
    combined_sentiments = {}
    for results in all_results:
        for sentiment in results:
            label = sentiment['label']
            score = sentiment['score']
            if label not in combined_sentiments:
                combined_sentiments[label] = []
            combined_sentiments[label].append(score)

    # Calcola la media per ciascuna etichetta
    avg_sentiments = []
    for label, scores in combined_sentiments.items():
        avg_score = sum(scores) / len(scores)
        avg_sentiments.append({'label': label, 'score': avg_score})

    # Trova il sentiment con il punteggio più alto
    best = max(avg_sentiments, key=lambda x: x['score'])

    return {
        "sentiment": best['label'],
        "score": best['score'],
        "sentiments": avg_sentiments
    }