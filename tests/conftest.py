from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from src.fast_zero.database import get_session
from src.fast_zero.db_models import User, table_registry


@pytest.fixture
def client(session: Session):
    """
    A fixture that creates a TestClient for the app overring
    real data with test data.
    """

    def get_session_override():
        return session

    # Setup: Create a new TestClient instance
    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client  # This is where the test runs

    # Teardown: Clear the database after the test is complete
    app.dependency_overrides.clear()


@pytest.fixture
def user(session: Session):
    user = User(
        username='test_user',
        email='test_email@test.com',
        password='any_password',
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


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
