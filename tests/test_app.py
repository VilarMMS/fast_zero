from http import HTTPStatus


def test_read_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'message': 'Welcome to Fast Zero'}


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'testusername',
            'password': 'password',
            'email': 'test@test.com',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'testusername',
        'email': 'test@test.com',
        'id': 1,
    }


def test_read_users(client):
    # Arrange: Create a user so the database is not empty.
    client.post(
        '/users/',
        json={
            'username': 'testusername',
            'password': 'password',
            'email': 'test@test.com',
        },
    )

    # Act
    response = client.get('/users/')

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'username': 'testusername',
                'email': 'test@test.com',
                'id': 1
            }
        ]
    }


def test_update_user(client):
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


def test_delete_user(client):
    # Arrange: Create a user to be deleted.
    client.post(
        '/users/',
        json={
            'username': 'test_to_delete',
            'password': 'password',
            'email': 'delete@test.com',
        },
    )

    # Act
    response = client.delete('/users/1')

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message':
                               'User test_to_delete deleted successfully'}


def test_read_user_by_id(client):
    # Arrange
    client.post(
        '/users/',
        json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        },
    )

    # Act
    response = client.get('/users/1')

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'testuser',
        'email': 'test@example.com',
    }


def test_read_user_by_id_not_found(client):
    # Act
    response = client.get('/users/999')

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user_not_found(client):
    # Act
    response = client.put(
        '/users/999',
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
