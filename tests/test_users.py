from dataclasses import asdict
from http import HTTPStatus

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.db_models import User
from fast_zero.schemas import UserPublic


def test_read_users(user, client, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    # Data do assert
    username = 'test'
    email = 'email@gmail.com'
    password = 'any_password'

    with mock_db_time() as time:
        new_user = User(username=username, email=email, password=password)
        session.add(new_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.username == 'test')
        )

        assert asdict(user) == {
            'id': 1,
            'username': username,
            'email': email,
            'created_at': time,
            'updated_at': time,
            'password': password,
            'todos': []
        }


def test_update_user(client, user, token):
    # Act
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'testusername_put',
            'email': 'test_put@test.com',
            'password': 'new_password',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'testusername_put',
        'email': 'test_put@test.com',
        'id': 1,
    }


def test_update_user_with_wrong_id(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@email.com',
            'password': 'password',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permission'}


def test_update_integrity_error(client, user, token):
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
        headers={'Authorization': f'Bearer {token}'},
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


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': f'User {user.username} deleted successfully'
    }


def test_delete_user_with_wrong_id(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permission'}


# TEST CASE: USER NOT FOUND !


def test_read_user_when_id_not_found(client):
    # Act
    response = client.get('/users/2')

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
