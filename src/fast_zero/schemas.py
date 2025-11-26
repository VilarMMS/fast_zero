from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fast_zero.db_models import TodoState


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UsersList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterUsers(BaseModel):
    limit: int = Field(ge=1, default=10)
    offset: int = Field(ge=0, default=0)


class FilterToDo(FilterUsers):
    title: str | None = Field(default=None, min_length=3)
    description: str | None = None
    state: TodoState | None = None


class ToDoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None


class TodoSchema(BaseModel):
    title: str
    description: str | None = None
    state: TodoState = Field(default=TodoState.todo)


class TodoPublic(TodoSchema):
    id: int


class TodosList(BaseModel):
    todos: list[TodoPublic]
