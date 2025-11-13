from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.db_models import User, table_registry
from fast_zero.security import Settings, get_password_harsh


@pytest.fixture
def client(session: AsyncSession):
    """
    A fixture that creates a TestClient for the app overriding
    real data with test data.
    """

    def get_session_override():
        print(
            f'get_session_override called, yielding session id: {id(session)}'
        )
        yield session

    # Setup: Create a new TestClient instance
    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    # Teardown: Clear the database after the test is complete
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    clean_password = 'any_password'
    user = User(
        username='test_user',
        email='test_email@test.com',
        password=get_password_harsh(clean_password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = clean_password
    return user


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(model=User, time=datetime.now()):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(User, 'before_insert', fake_time_hook)

    yield time

    event.remove(User, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )
    return response.json()['access_token']


@pytest.fixture
def settings():
    return Settings()
