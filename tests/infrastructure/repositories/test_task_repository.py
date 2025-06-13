import boto3
import pytest
from moto import mock_aws

from src.domains.models.task import Task, TaskPriority, TaskStatus
from src.exceptions.errors import DataAccessError, DataNotFoundError, InvalidParameterError
from src.infrastructure.repositories.task_repository import TaskDynamoDBRepository

# filepath: src/repositories/test_task_repository.py

TABLE_NAME = "Tasks"


@pytest.fixture
def dynamodb_mock():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        yield table


@pytest.fixture
def repository(dynamodb_mock):
    return TaskDynamoDBRepository(TABLE_NAME)


def test_create_task(repository):
    # Arrange
    task = Task(
        id="550e8400-e29b-41d4-a716-446655440001",
        title="Task 1",
        description="Description 1",
        due_date="2025-12-31",
        status="TODO",
        priority="HIGH",
    )

    # Act
    repository.create_task(task)

    # Assert

    get_result = repository.get_task("550e8400-e29b-41d4-a716-446655440001")
    assert str(get_result.id) == "550e8400-e29b-41d4-a716-446655440001"

    with pytest.raises(DataNotFoundError):
        repository.get_task("non-existent-id")


def test_delete_task(repository, dynamodb_mock):
    # Arrange
    dynamodb_mock.put_item(
        Item={
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "title": "Task 1",
            "description": "Description 1",
            "due_date": "2025-12-31",
            "status": "TODO",
            "priority": "HIGH",
        }
    )

    # Act
    repository.delete_task("550e8400-e29b-41d4-a716-446655440001")

    # Assert
    with pytest.raises(DataNotFoundError):
        repository.delete_task("550e8400-e29b-41d4-a716-446655440001")


def test_get_task(repository, dynamodb_mock):
    # Arrange
    dynamodb_mock.put_item(
        Item={
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "title": "Task 1",
            "description": "Description 1",
            "due_date": "2025-12-31",
            "status": "TODO",
            "priority": "HIGH",
        }
    )

    # Act
    task = repository.get_task("550e8400-e29b-41d4-a716-446655440001")

    # Assert
    assert str(task.id) == "550e8400-e29b-41d4-a716-446655440001"
    assert task.title == "Task 1"
    assert task.description == "Description 1"


def test_update_task(repository, dynamodb_mock):
    # Arrange
    dynamodb_mock.put_item(
        Item={
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "title": "Task 1",
            "description": "Description 1",
            "priority": "HIGH",
            "status": "TODO",
            "due_date": "2025-12-31",
        }
    )
    updated_task = Task(
        id="550e8400-e29b-41d4-a716-446655440001",
        title="Updated Task",
        description="Updated Description",
        due_date="2025-12-31",  # 変更しない
        priority=TaskPriority.LOW,
        status=TaskStatus.DONE,
    )

    # Act
    repository.update_task(updated_task)

    # Assert
    result = repository.get_task("550e8400-e29b-41d4-a716-446655440001")
    assert result.title == "Updated Task"
    assert result.description == "Updated Description"
    assert result.priority == TaskPriority.LOW
    assert result.status == TaskStatus.DONE

    # そのまま
    assert result.due_date == "2025-12-31"

    # 存在しないIDを更新しようとするとエラー ===================
    non_exist_updated_task = Task(
        id="550e8400-e29b-41d4-a716-446655440999",
        title="Updated Task",
        description="Updated Description",
        priority=TaskPriority.LOW,
        status=TaskStatus.DONE,
    )
    with pytest.raises(DataNotFoundError):
        repository.update_task(non_exist_updated_task)


def test_list_tasks(repository, dynamodb_mock):
    # Arrange
    item_1 = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Task 1",
        "description": "Description 1",
        "due_date": "2025-12-31",
        "status": "TODO",
        "priority": "HIGH",
    }
    item_2 = {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "Task 2",
        "description": "Description 2",
        "due_date": "2025-12-31",
        "status": "DONE",
        "priority": "LOW",
    }
    dynamodb_mock.put_item(Item=item_1)
    dynamodb_mock.put_item(Item=item_2)

    # Act
    tasks = repository.list_tasks()

    # Assert
    assert len(tasks) == 2
    assert str(tasks[0].id) == item_1["id"]
    assert tasks[0].title == item_1["title"]
    assert str(tasks[1].id) == item_2["id"]
    assert tasks[1].title == item_2["title"]
