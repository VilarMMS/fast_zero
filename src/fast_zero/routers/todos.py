from typing import Annotated
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fast_zero.database import get_session
from fast_zero.db_models import ToDo, User
from fast_zero.schemas import (
    FilterToDo,
    TodoPublic,
    TodoSchema,
    TodosList,
    ToDoUpdate,
    Message)
from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@router.post('/', response_model=TodoPublic)
async def create_todo(todo: TodoSchema, session: Session, user: CurrentUser):
    db_todo = ToDo(
        title=todo.title,
        description=todo.description,
        user_id=user.id,
        state=todo.state,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodosList)
async def list_todos(
    todos_filters: Annotated[FilterToDo, Query()],
    session: Session,
    user: CurrentUser,
):
    query = select(ToDo).where(ToDo.user_id == user.id)

    if todos_filters.title:
        query = query.filter(ToDo.title.contains(
            todos_filters.title))

    if todos_filters.description:
        query = query.filter(ToDo.description.contains(
            todos_filters.description))

    if todos_filters.state:
        query = query.filter(ToDo.state == todos_filters.state)

    todos = await session.scalars(
        query.limit(todos_filters.limit).offset(todos_filters.offset))

    return {'todos': todos.all()}


@router.delete('/{todo_id}', response_model=Message)
async def delete_todo(todo_id: int, session: Session, user: CurrentUser):
    todo = await session.scalar(
        select(ToDo).where(ToDo.user_id == user.id, ToDo.id == todo_id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found'
        )

    await session.delete(todo)
    await session.commit()

    return {'message': 'Task deleted successfully'}


@router.patch('/{todo_id}', response_model=TodoPublic)
async def patch_todo(todo_id: int,
                     session: Session,
                     user: CurrentUser,
                     todo: ToDoUpdate):

    db_todo = await session.scalar(
        select(ToDo).where(ToDo.user_id == user.id, ToDo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found'
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo