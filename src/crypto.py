import os
from cryptography.fernet import Fernet

def _fernet() -> Fernet:
    key = os.environ.get("DROP_KEY")
    if not key:
        raise RuntimeError("DROP_KEY is not set")
    return Fernet(key)

def check_key() -> None:
    _fernet()

def encrypt(text: str) -> bytes:
    return _fernet().encrypt(text.encode())

def decrypt(data: bytes) -> str:
    return _fernet().decrypt(data).decode()
