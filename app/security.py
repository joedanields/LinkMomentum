from cryptography.fernet import Fernet, InvalidToken
import os
from dotenv import load_dotenv

load_dotenv()

# Use FERNET_KEY from environment for deterministic encryption in prod.
# If not provided, generate one (not recommended for production because it won't persist).
_FERNET_KEY = os.getenv("FERNET_KEY")
if not _FERNET_KEY:
    _FERNET_KEY = Fernet.generate_key().decode()

fernet = Fernet(_FERNET_KEY.encode())


def encrypt_text(plain: str) -> str:
    if plain is None:
        return None
    token = fernet.encrypt(plain.encode())
    return token.decode()


def decrypt_text(token: str) -> str:
    if token is None:
        return None
    try:
        return fernet.decrypt(token.encode()).decode()
    except InvalidToken:
        return None
