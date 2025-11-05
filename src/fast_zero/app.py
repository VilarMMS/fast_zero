from http import HTTPStatus

from fastapi import Depends, FastAPI
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import (
    get_session,
    raise_conflict,
    raise_user_not_found,
)
from fast_zero.db_models import User
from fast_zero.schemas import Message, UserPublic, UserSchema, UsersList

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Welcome to Fast Zero'}


@app.get('/users/', response_model=UsersList)
def read_users(
    session: Session = Depends(get_session), limit: int = 10, offset: int = 0
):
    users = session.scalars(select(User).limit(limit).offset(offset)).all()
    return {'users': users}


@app.get('/users/{user_id}', response_model=UserPublic)
def read_single_user(user_id: int, session: Session = Depends(get_session)):
    user_query = session.scalar(select(User).where(User.id == user_id))

    if user_query is None:
        raise_user_not_found()
    else:
        return user_query


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            or_(User.username == user.username, User.email == user.email)
        )
    )
    if db_user is not None:
        raise_conflict()
    else:
        db_user = User(
            username=user.username, email=user.email, password=user.password
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return db_user


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):
    # Verify if user exists
    db_user = session.scalar(select(User).where(User.id == user_id))

    if db_user is None:
        raise_user_not_found()
    else:
        try:
            db_user.username = user.username
            db_user.email = user.email
            db_user.password = user.password

            session.add(db_user)
            session.commit()
            session.refresh(db_user)

            return db_user

        except IntegrityError:
            raise_conflict()


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    # Verify if user exists
    db_user = session.scalar(select(User).where(User.id == user_id))

    if db_user is None:
        raise_user_not_found()

    username = db_user.username
    session.delete(db_user)
    session.commit()

    return {'message': f'User {username} deleted successfully'}
