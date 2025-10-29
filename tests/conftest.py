import pytest
from fastapi.testclient import TestClient

from fast_zero.app import app, database


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
