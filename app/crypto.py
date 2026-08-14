import base64
import hashlib
from cryptography.fernet import Fernet
from app.config import TOKEN_ENCRYPTION_KEY, SESSION_SECRET

def _fernet():
    seed = TOKEN_ENCRYPTION_KEY or SESSION_SECRET
    key = base64.urlsafe_b64encode(hashlib.sha256(seed.encode()).digest())
    return Fernet(key)

def encrypt_text(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()

def decrypt_text(value: str) -> str:
    return _fernet().decrypt(value.encode()).decode()
