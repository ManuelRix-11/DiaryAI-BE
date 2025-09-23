from typing import List, Optional, Dict, Any
from pydantic import EmailStr

from app.models.user import User
from app.core.security import hash_password


async def create_user(username: str, email: EmailStr, password: str) -> User:
    """
    Crea un nuovo utente nel sistema.

    Args:
        username: Nome utente
        email: Indirizzo email (deve essere valido e unico)
        password: Password in chiaro che verrà hashata prima del salvataggio

    Returns:
        L'oggetto User creato
    """
    hashed_password = hash_password(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    await user.insert()
    return user


async def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Recupera un utente tramite il suo ID.

    Args:
        user_id: ID dell'utente da recuperare

    Returns:
        L'oggetto User se trovato, altrimenti None
    """
    return await User.get(user_id)


async def get_user_by_email(email: EmailStr) -> Optional[User]:
    """
    Recupera un utente tramite il suo indirizzo email.

    Args:
        email: Indirizzo email dell'utente

    Returns:
        L'oggetto User se trovato, altrimenti None
    """
    return await User.find_one(User.email == email)


async def list_users() -> List[User]:
    """
    Recupera tutti gli utenti dal database.

    Returns:
        Lista di tutti gli utenti
    """
    return await User.find_all().to_list()


async def update_user(user_id: str, data: Dict[str, Any]) -> Optional[User]:
    """
    Aggiorna i dati di un utente esistente.

    Args:
        user_id: ID dell'utente da aggiornare
        data: Dizionario contenente i campi da aggiornare
              Nota: se "password" è presente, verrà hashata automaticamente

    Returns:
        L'oggetto User aggiornato se trovato, altrimenti None
    """
    user = await User.get(user_id)
    if not user:
        return None

    # Gestione speciale per la password
    if "password" in data:
        data["hashed_password"] = hash_password(data.pop("password"))

    # Filtra i campi con valore None per evitare di sovrascrivere con null
    update_data = {k: v for k, v in data.items() if v is not None}

    if update_data:
        # Aggiorna i campi dell'utente
        await user.set(update_data)
        # Aggiorna l'oggetto locale
        user = await User.get(user_id)

    return user


async def delete_user(user_id: str) -> bool:
    """
    Elimina un utente dal sistema.

    Args:
        user_id: ID dell'utente da eliminare

    Returns:
        True se l'eliminazione è avvenuta con successo, False se l'utente non esiste
    """
    try:
        user = await User.get(user_id)
        if not user:
            return False
        await user.delete()
        return True
    except Exception as e:
        print(f"Errore durante l'eliminazione dell'utente: {str(e)}")
        return False


async def authenticate_user(email: EmailStr, password: str) -> Optional[User]:
    """
    Autentica un utente verificando email e password.

    Args:
        email: Indirizzo email dell'utente
        password: Password in chiaro da verificare

    Returns:
        L'oggetto User se l'autenticazione ha successo, altrimenti None
    """
    from app.core.security import verify_password

    user = await get_user_by_email(email)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


async def search_users(search_term: str) -> List[User]:
    """
    Cerca utenti per nome utente o email.

    Args:
        search_term: Termine di ricerca da applicare a username o email

    Returns:
        Lista di utenti che corrispondono al criterio di ricerca
    """
    # Utilizzo di espressioni regolari per ricerca parziale
    import re
    pattern = re.compile(f".*{search_term}.*", re.IGNORECASE)

    users = await User.find({
        "$or": [
            {"username": {"$regex": pattern}},
            {"email": {"$regex": pattern}}
        ]
    }).to_list()

    return users