import base64,hashlib
from cryptography.fernet import Fernet
from app.config import TOKEN_ENCRYPTION_KEY,SESSION_SECRET
def _f():
    seed=TOKEN_ENCRYPTION_KEY or SESSION_SECRET
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(seed.encode()).digest()))
def encrypt_text(v): return _f().encrypt(v.encode()).decode()
def decrypt_text(v): return _f().decrypt(v.encode()).decode()
