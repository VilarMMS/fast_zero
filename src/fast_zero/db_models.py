from __future__ import annotations
from datetime import datetime
from enum import Enum
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


class TodoState(str, Enum):
    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    todos: Mapped[list['ToDo']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='selectin',
        init=False,
    )


@table_registry.mapped_as_dataclass
class ToDo:
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    # --- FIX #3: Add a relationship back to the single User owner ---
    user: Mapped['User'] = relationship(
        back_populates='todos',
        lazy='selectin',
        init=False,
    )

    state: Mapped[TodoState] = mapped_column(
        default=TodoState.todo, server_default=TodoState.todo.value
    )

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
