from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_zero.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)


async def get_session():  # pragma: no cover
    async with AsyncSession(
        engine, expire_on_commit=False
    ) as session:  # pragma: no cover
        yield session  # pragma: no cover


def raise_user_not_found():
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail='User not found'
    )


def raise_conflict():
    raise HTTPException(
        status_code=HTTPStatus.CONFLICT,
        detail='Username or email already registered',
    )


def raise_unauthorized():
    raise HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Incorrect username or password',
    )


def raise_credentials_expection():
    raise HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )


def raise_forbidden():
    raise HTTPException(
        status_code=HTTPStatus.FORBIDDEN,
        detail='Not enough permission',
    )
