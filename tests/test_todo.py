import factory
import factory.fuzzy
import pytest
from fast_zero.db_models import ToDo, TodoState
from http import HTTPStatus


class ToDoFactory(factory.Factory):
    class Meta:
        model = ToDo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, token):
    response = client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test ToDo',
            'description': 'This is a test ToDo item.',
            'state': 'draft',
        },
    )
    assert response.json() == {
        'id': 1,
        'title': 'Test ToDo',
        'description': 'This is a test ToDo item.',
        'state': 'draft',
    }


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(session, client, user, token):

    # arrange
    excepted_todos = 5
    session.add_all(
        ToDoFactory.create_batch(excepted_todos, user_id=user.id)
    )
    await session.commit()

    # act
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == excepted_todos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    session, client, user, token
):
    # Arrange: Create a larger batch of items to test pagination against.
    total_todos_created = 5
    session.add_all(
        ToDoFactory.create_batch(total_todos_created, user_id=user.id)
    )
    await session.commit()

    # We expect 2 items back from this specific query
    expected_todos_in_response = 2

    # Act: Get the second "page" of 2 items (by skipping the first 2)
    response = client.get(
        '/todos?limit=2&offset=2',  # Querying for items 3 and 4
        headers={'Authorization': f'Bearer {token}'},
    )

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos_in_response


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos_filtered_title(
    session, client, user, token):

    # arrange
    excepted_todos = 5
    title_todo = "Test todo 1"
    endpoint = F'/todos/?title={title_todo}'

    # Adding todos with the same title to test filtering
    session.add_all(
        ToDoFactory.create_batch(excepted_todos,
                                 user_id=user.id,
                                 title=title_todo)
    )

    # Adding todos with different title
    session.add_all(
        ToDoFactory.create_batch(excepted_todos,
                                    user_id=user.id)
    )

    await session.commit()

    # act
    response = client.get(
        endpoint,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == excepted_todos


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos_filtered_description(
    session, client, user, token):

    # arrange
    excepted_todos = 5
    letters_count_to_filter_description = 4
    description_todo = "Test description"
    endpoint = F'/todos/?description={description_todo[
        :letters_count_to_filter_description]}'

    # Adding todos with the same title to test filtering
    session.add_all(
        ToDoFactory.create_batch(excepted_todos,
                                 user_id=user.id,
                                 description=description_todo)
    )

    # Adding todos with different title
    session.add_all(
        ToDoFactory.create_batch(excepted_todos,
                                    user_id=user.id)
    )

    await session.commit()

    # act
    response = client.get(
        endpoint,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == excepted_todos


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos_filtered_state(
    session, client, user, token):

    # arrange
    excepted_todos = 5
    state_todo = "draft"
    endpoint = F'/todos/?state={state_todo}'

    # Adding todos with the same title to test filtering
    session.add_all(
        ToDoFactory.create_batch(excepted_todos,
                                 user_id=user.id,
                                 state=TodoState.draft)
    )

    # Adding todos with different title
    session.add_all(
        ToDoFactory.create_batch(excepted_todos,
                                    user_id=user.id)
    )

    await session.commit()

    # act
    response = client.get(
        endpoint,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == excepted_todos


@pytest.mark.asyncio
async def test_delete_todo_error(client, token):

    response = client.delete(
        '/todos/1111111',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_delete_todo(client, session, user, token):

    todo = ToDoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task deleted successfully'}


@pytest.mark.asyncio
async def test_delete_other_user_todo(client,
                                      session,
                                      other_user,
                                      token):

    todo_other_user = ToDoFactory(user_id=other_user.id)
    session.add(todo_other_user)
    await session.commit()

    response = client.delete(
        f'/todos/{todo_other_user.id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_delete_patch_error(client, token):

    response = client.delete(
        '/todos/1111111',
        json={},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_patch_todo(client, session, user, token):
    todo = ToDoFactory(user_id=user.id)

    todo_title = 'Updated Title'
    todo_description = 'Updated Description'
    todo_state = 'doing'

    session.add(todo)
    await session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={
            'title': todo_title,
            'description': todo_description,
            'state': todo_state,
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == todo_title
    assert response.json()['description'] == todo_description
    assert response.json()['state'] == todo_state
