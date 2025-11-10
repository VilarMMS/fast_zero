from http import HTTPStatus

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import (
    get_session,
    raise_conflict,
    raise_forbidden,
    raise_unauthorized,
    raise_user_not_found,
)
from fast_zero.db_models import User
from fast_zero.schemas import Message, Token, UserPublic, UserSchema, UsersList
from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_harsh,
    verify_password,
)

app = FastAPI(title='Minha API da hora')


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Welcome to Fast Zero'}


@app.get('/users/', response_model=UsersList)
def read_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0,
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
            username=user.username,
            email=user.email,
            password=get_password_harsh(user.password),
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return db_user


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise_forbidden()

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_harsh(user.password)

        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise_conflict()


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int,
                session: Session = Depends(get_session),
                current_user: User = Depends(get_current_user)):

    if current_user.id != user_id:
        raise_forbidden()
    else:
        username = current_user.username
        session.delete(current_user)
        session.commit()

    return {'message': f'User {username} deleted successfully'}


# Generate token for login
@app.post('/token', response_model=Token)
def login_to_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if user is None:
        raise_unauthorized()

    if not verify_password(form_data.password, user.password):
        raise_unauthorized()

    access_token = create_access_token({'sub': user.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}
