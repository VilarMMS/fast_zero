from dataclasses import asdict

from sqlalchemy import select

from src.fast_zero.db_models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='testuser',
            email='test@test.com',
            password='securepassword',
        )

        session.add(new_user)
        session.commit()

        # Scalar method to convert database metadata to python
        user = session.scalar(select(User).where(User.username == 'testuser'))

        assert asdict(user) == {
            'id': 1,
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'securepassword',
            'created_at': time,
        }
