import base64
import hashlib

from cryptography.fernet import Fernet
from django.conf import settings


def _fernet() -> Fernet:
    key = hashlib.sha256(settings.FIELD_ENCRYPTION_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_value(plain: str) -> str:
    if not plain:
        return ""
    return _fernet().encrypt(plain.encode()).decode()


def decrypt_value(token: str) -> str:
    if not token:
        return ""
    return _fernet().decrypt(token.encode()).decode()
