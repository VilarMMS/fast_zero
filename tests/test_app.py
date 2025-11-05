from http import HTTPStatus

from src.fast_zero.schemas import UserPublic


def test_read_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'message': 'Welcome to Fast Zero'}


def test_read_users_when_db_is_empty(client):
    reponse = client.get('/users/')

    assert reponse.status_code == HTTPStatus.OK
    assert reponse.json() == {'users': []}


def test_read_users_when_db_contains_data(client, user):

    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_create_user(client, mock_db_time):

    # Test variables
    username = 'alice'
    email = 'test@gmail.com'
    password = 'password'

    response = client.post(
        '/users/',
        json={'username': username, 'email': email, 'password': password},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': username,
        'email': email,
        'created_at': time,
        'updated_at': time,
    }


def test_update_user(client, user):
    # Arrange: Create a user to be updated.
    client.post(
        '/users/',
        json={
            'username': 'testusername',
            'password': 'password',
            'email': 'test@test.com',
        },
    )

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


def test_delete_user(client, user):

    response = client.delete('/users/1')

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': f'User {user.username} deleted successfully'}


def test_update_integrity_error(client, user):
    
    # Create new user
    client.post('/users/',
                json={
                    'username': 'conflict_user',
                    'email': 'conflict_user@email.com',
                    'password': 'password'
                    }
                )
    
    # Try to update existing user with same username and email
    response_update = client.put('/users/{user_id}',
                                json={
                    'username': 'conflict_user',
                    'email': 'conflict_user@email.com',
                    'password': 'password'
                    }
                    )
    
    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or email already registered'
    }

# def test_read_user_by_id(client):
#     # Arrange
#     client.post(
#         '/users/',
#         json={
#             'username': 'testuser',
#             'email': 'test@example.com',
#             'password': 'password123',
#         },
#     )

#     # Act
#     response = client.get('/users/1')

#     # Assert
#     assert response.status_code == HTTPStatus.OK
#     assert response.json() == {
#         'id': 1,
#         'username': 'testuser',
#         'email': 'test@example.com',
#     }


# def test_read_user_by_id_not_found(client):
#     # Act
#     response = client.get('/users/999')

#     # Assert
#     assert response.status_code == HTTPStatus.NOT_FOUND
#     assert response.json() == {'detail': 'User not found'}


# def test_update_user_not_found(client):
#     # Act
#     response = client.put(
#         '/users/999',
#         json={
#             'username': 'testusername_put',
#             'email': 'test_put@test.com',
#             'password': 'new_password',
#         },
#     )

#     # Assert
#     assert response.status_code == HTTPStatus.NOT_FOUND
#     assert response.json() == {'detail': 'User not found'}


# def test_delete_user_not_found(client):
#     # Act
#     response = client.delete('/users/999')

#     # Assert
#     assert response.status_code == HTTPStatus.NOT_FOUND
#     assert response.json() == {'detail': 'User not found'}
