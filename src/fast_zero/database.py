from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_zero.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


def raise_user_not_found():
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail='User not found'
    )


def raise_conflict():
    raise HTTPException(
        status_code=HTTPStatus.CONFLICT,
        detail='Username or email already registered',
    )
