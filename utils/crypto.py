# utils/crypto.py
from cryptography.fernet import Fernet
from django.conf import settings

def _get_fernet() -> Fernet:
    return Fernet(settings.FERNET_KEY.encode())

def encrypt_text(plain: str) -> str:
    return _get_fernet().encrypt(plain.encode()).decode()

def decrypt_text(token: str) -> str:
    return _get_fernet().decrypt(token.encode()).decode()
