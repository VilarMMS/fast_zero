from src.fast_zero.db_models import User


def test_create_user():
    user = User(
        username='testuser',
        email='test@test.com',
        password='securepassword'
    )
    assert user.username == 'testuser'
