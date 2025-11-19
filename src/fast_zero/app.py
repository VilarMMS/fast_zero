from http import HTTPStatus

from fastapi import FastAPI

from fast_zero.routers import auth, users
from fast_zero.schemas import Message

app = FastAPI(title='Minha API da hora')

app.include_router(users.router)
app.include_router(auth.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
async def read_root():
    return {'message': 'Welcome to Fast Zero'}
