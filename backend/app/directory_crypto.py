import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from .config import settings


def _fernet():
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.jwt_secret.encode('utf-8')).digest())
    return Fernet(key)


def encrypt_directory_password(value: str) -> str:
    return _fernet().encrypt(value.encode('utf-8')).decode('ascii')


def decrypt_directory_password(value: str) -> str:
    if not value:
        return ''
    try:
        return _fernet().decrypt(value.encode('ascii')).decode('utf-8')
    except InvalidToken as exc:
        raise RuntimeError('AD 管理密码无法解密，请重新保存配置') from exc
