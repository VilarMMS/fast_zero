from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from fast_zero.app import app, database
from src.fast_zero.db_models import User, table_registry


@pytest.fixture
def client():
    """
    A fixture that creates a TestClient for the app and cleans up the
    database after each test.
    """
    # Setup: Create a new TestClient instance
    with TestClient(app) as client:
        yield client  # This is where the test runs

    # Teardown: Clear the database after the test is complete
    database.clear()


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@contextmanager
def _mock_db_time(model=User, time=datetime.now()):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

    event.listen(User, 'before_insert', fake_time_hook)

    yield time

    event.remove(User, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time
