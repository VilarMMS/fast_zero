from dataclasses import asdict
from http import HTTPStatus

from sqlalchemy import select

from fast_zero.db_models import User
from fast_zero.schemas import UserPublic


def test_read_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'message': 'Welcome to Fast Zero'}


def test_read_users_when_db_is_empty(client):
    reponse = client.get('/users/')

    assert reponse.status_code == HTTPStatus.OK
    assert reponse.json() == {'users': []}


def test_read_users_when_db_contains_data(session, user, client):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_create_user(session, mock_db_time):
    # Data do assert
    username = 'test'
    email = 'email@gmail.com'
    password = 'any_password'

    with mock_db_time() as time:
        new_user = User(username=username, email=email, password=password)
        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == 'test'))

        assert asdict(user) == {
            'id': 1,
            'username': username,
            'email': email,
            'created_at': time,
            'updated_at': time,
            'password': password,
        }


def test_update_user(client, user):
    # Act
    response = client.put(
        '/users/1',
        json={
            'username': 'testusername_put',
            'email': 'test_put@test.com',
            'password': 'new_password',
        },
    )

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'testusername_put',
        'email': 'test_put@test.com',
        'id': 1,
    }


def test_update_integrity_error(client, user):
    # Create new user
    client.post(
        '/users/',
        json={
            'username': 'conflict_user',
            'email': 'conflict_user@email.com',
            'password': 'password',
        },
    )

    # Try to update existing user with same username and email
    response_update = client.put(
        f'/users/{user.id}',
        json={
            'username': 'conflict_user',
            'email': 'conflict_user@email.com',
            'password': 'password',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or email already registered'
    }


def test_delete_user(client, user):
    response = client.delete('/users/1')

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': f'User {user.username} deleted successfully'
    }


# TEST CASE: USER NOT FOUND !


def test_read_user_when_id_not_found(client):
    # Act
    response = client.get('/users/2')

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user_not_found(client):
    response = client.put(
        '/users/2',
        json={
            'username': 'testusername_put',
            'email': 'test_put@test.com',
            'password': 'new_password',
        },
    )

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user_not_found(client):
    # Act
    response = client.delete('/users/999')

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
