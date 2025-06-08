import boto3
import pytest
from moto import mock_aws

from src.exceptions.errors import DataAccessError, DataNotFoundError, InvalidParameterError
from src.repositories.task_repository import TaskDynamoDBRepository
from src.schemas.task import Task

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


def test_list_tasks(repository, dynamodb_mock):
    # Arrange
    dynamodb_mock.put_item(
        Item={
            "id": "1",
            "title": "Task 1",
            "description": "Description 1",
            "due_date": "2025-12-31",
            "status": "pending",
            "priority": "high",
        }
    )
    dynamodb_mock.put_item(
        Item={
            "id": "2",
            "title": "Task 2",
            "description": "Description 2",
            "due_date": "2025-12-31",
            "status": "completed",
            "priority": "low",
        }
    )

    # Act
    tasks = repository.list_tasks()

    # Assert
    assert len(tasks) == 2
    assert tasks[0].id == "1"
    assert tasks[0].title == "Task 1"
    assert tasks[1].id == "2"
    assert tasks[1].title == "Task 2"


def test_create_task(repository):
    # Arrange
    task = Task(id="1", title="Task 1", description="Description 1")

    # Act
    created_task = repository.create_task(task)

    # Assert
    assert created_task.id == "1"
    assert created_task.title == "Task 1"


def test_delete_task(repository, dynamodb_mock):
    # Arrange
    dynamodb_mock.put_item(Item={"id": "1", "title": "Task 1", "description": "Description 1"})

    # Act
    repository.delete_task("1")

    # Assert
    with pytest.raises(DataNotFoundError):
        repository.delete_task("1")


def test_get_task(repository, dynamodb_mock):
    # Arrange
    dynamodb_mock.put_item(
        Item={
            "id": "1",
            "title": "Task 1",
            "description": "Description 1",
            "due_date": "2025-12-31",
            "status": "pending",
            "priority": "high",
        }
    )

    # Act
    task = repository.get_task("1")

    # Assert
    assert task.id == "1"
    assert task.title == "Task 1"
    assert task.description == "Description 1"


def test_update_task(repository, dynamodb_mock):
    # Arrange
    dynamodb_mock.put_item(Item={"id": "1", "title": "Task 1", "description": "Description 1"})
    updated_task = {"title": "Updated Task", "description": "Updated Description"}

    # Act
    result = repository.update_task("1", updated_task)

    # Assert
    assert result.title == "Updated Task"
    assert result.description == "Updated Description"
