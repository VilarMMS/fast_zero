from datetime import datetime, timedelta
from http import HTTPStatus

from freezegun import freeze_time
from jwt import decode

from fast_zero.security import create_access_token
from fast_zero.settings import Settings

ACCESS_TOKEN_EXPIRE_MINUTES = Settings().ACCESS_TOKEN_EXPIRE_MINUTES


def test_jwt(settings):
    data = {'test': 'test'}

    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_jwt_invalid_token(client):
    response = client.delete(
        'users/1', headers={'Authorization': 'Bearer token invalid'}
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
        'users/1', headers={'Authorization': f'Bearer {token}'}
    )

    # (3) Assert that the request is unauthorized.
    # The 'get_current_user' function should fail to find a user with
    # 'wrong@email.com' and raise a credentials exception.
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_get_token_wrong_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrongpassword'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_get_token_wrong_email(client, user):
    response = client.post(
        '/auth/token',
        data={'username': 'wrong@email.com', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_token_expired_after_time(client, user):
    current_time = datetime.now()

    # Fix 1: Add minutes= parameter to timedelta
    lapsed_time = current_time + timedelta(
        minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES + 1
    )

    with freeze_time(current_time):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        token = response.json()['access_token']
        assert response.status_code == HTTPStatus.OK

    with freeze_time(lapsed_time):
        protected_response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )

        assert protected_response.status_code == HTTPStatus.UNAUTHORIZED
        assert protected_response.json() == {
            'detail': 'Could not validate credentials'
        }


def test_refresh_token(client, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'


def test_token_expired_dont_refresh(client, user):
    current_time = datetime.now()

    # Fix 1: Add minutes= parameter to timedelta
    lapsed_time = current_time + timedelta(
        minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES + 1
    )

    with freeze_time(current_time):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        token = response.json()['access_token']
        assert response.status_code == HTTPStatus.OK

    with freeze_time(lapsed_time):
        response = client.post(
            '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
