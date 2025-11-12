from http import HTTPStatus

from jwt import decode

from fast_zero.security import create_access_token


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
