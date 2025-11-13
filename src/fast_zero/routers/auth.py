from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import (
    get_session,
    raise_unauthorized,
)
from fast_zero.db_models import User
from fast_zero.schemas import Token
from fast_zero.security import (
    create_access_token,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

UserSession = Annotated[AsyncSession, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


# Generate token for login
@router.post('/token', response_model=Token)
async def login_to_access_token(form_data: OAuth2Form, session: UserSession):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if user is None:
        raise_unauthorized()

    if not verify_password(form_data.password, user.password):
        raise_unauthorized()

    access_token = create_access_token({'sub': user.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}
