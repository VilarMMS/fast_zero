from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session, raise_credentials_expection
from fast_zero.db_models import User

SECRET_KEY = 'your-secret-key'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ouath2_scheme = OAuth2PasswordBearer(tokenUrl='token')

pwd_context = PasswordHash.recommended()


def get_password_harsh(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    datetime_now = datetime.now(tz=ZoneInfo('UTC'))
    expire = datetime_now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})

    encoeded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoeded_jwt


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(ouath2_scheme),
):
    try:
        payload = decode(token, SECRET_KEY, algorithms=ALGORITHM)
        subject_email = payload.get('sub')
        if subject_email is None:
            raise_credentials_expection()

    except DecodeError:
        raise_credentials_expection()

    user = session.scalar(select(User).where(User.email == subject_email))

    if user is None:
        raise_credentials_expection()

    else:
        return user
