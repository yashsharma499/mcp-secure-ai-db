from passlib.context import CryptContext

from app.core.config import get_settings


_settings = get_settings()

_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=_settings.bcrypt_rounds
)


def hash_password(password: str) -> str:
    if not password or not isinstance(password, str):
        raise ValueError("Invalid password")
    try:
        return _pwd_context.hash(password)
    except Exception as e:
        raise RuntimeError("Failed to hash password") from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def hash_refresh_token(token: str) -> str:
    if not token or not isinstance(token, str):
        raise ValueError("Invalid refresh token")
    try:
        return _pwd_context.hash(token)
    except Exception as e:
        raise RuntimeError("Failed to hash refresh token") from e


def verify_refresh_token(token: str, hashed_token: str) -> bool:
    if not token or not hashed_token:
        return False
    try:
        return _pwd_context.verify(token, hashed_token)
    except Exception:
        return False
