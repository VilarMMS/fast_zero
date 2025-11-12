from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import (
    get_session,
    raise_conflict,
    raise_forbidden,
    raise_user_not_found,
)
from fast_zero.db_models import User
from fast_zero.schemas import (
    FilterUsers,
    Message,
    UserPublic,
    UserSchema,
    UsersList,
)
from fast_zero.security import (
    get_current_user,
    get_password_harsh,
)

router = APIRouter(prefix='/users', tags=['users'])
UserSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/', response_model=UsersList)
def read_users(
    session: UserSession,
    current_user: CurrentUser,
    filter_users: Annotated[FilterUsers, Query()],
):
    users = session.scalars(
        select(User).limit(filter_users.limit).offset(filter_users.offset)
    ).all()
    return {'users': users}


@router.get('/{user_id}', response_model=UserPublic)
def read_single_user(user_id: int, session: UserSession):
    user_query = session.scalar(select(User).where(User.id == user_id))

    if user_query is None:
        raise_user_not_found()
    else:
        return user_query


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: UserSession):
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


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: UserSession,
    current_user: CurrentUser,
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


@router.delete('/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: UserSession,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise_forbidden()
    else:
        username = current_user.username
        session.delete(current_user)
        session.commit()

    return {'message': f'User {username} deleted successfully'}
