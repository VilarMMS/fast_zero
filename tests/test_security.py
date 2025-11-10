from http import HTTPStatus
from jwt import decode

from fast_zero.security import ALGORITHM, SECRET_KEY, create_access_token


def test_jwt():
    data = {'test': 'test'}

    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=ALGORITHM)

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_jwt_invalid_token(client):
    response = client.delete(
        'users/1',
        headers={'Authorization': 'Bearer token invalid'}
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_wrong_subject_email(client):
    """
    Test case for when a JWT token has a valid signature but contains a
    subject email that does not correspond to any user in the database.
    """
    # (1) Create a token with a subject ('sub') that is not in the database.
    # The 'user' fixture is not needed here because we want to simulate a
    # user that does not exist.
    token = create_access_token(data={'sub': 'wrong@email.com'})

    # (2) Make a request to a protected endpoint with this token.
    response = client.delete(
        'users/1',
        headers={'Authorization': f'Bearer {token}'}
    )

    # (3) Assert that the request is unauthorized.
    # The 'get_current_user' function should fail to find a user with
    # 'wrong@email.com' and raise a credentials exception.
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_user_not_found(client):
    """
    Tests that a valid token for a non-existent user is rejected.

    This covers the case where the JWT is correctly signed and not expired,
    but the email in its 'sub' claim does not match any user in the database.
    """
    # The `client` fixture provides a clean, empty database for this test.
    # We do NOT use the `user` fixture, ensuring no user exists yet.

    # 1. Create a valid token with a subject for a user who is not in the DB.
    token = create_access_token(data={'sub': 'nonexistent.user@example.com'})

    # 2. Make a request to a protected endpoint using this token.
    # The endpoint path itself ('/users/1') doesn't matter, only that it's protected.
    # The application will check for the user before it tries to find user with ID 1.
    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'}
    )

    # 3. Assert that the request is unauthorized.
    # The `get_current_user` dependency should fail to find the user in the
    # database and raise a 401 exception.
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}