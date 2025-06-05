import logging

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

from ..exception.errors import DataAccessError, DataNotFoundError, InvalidParameterError
from ..schemas.task import Task

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class TaskDynamoDBRepository:
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def list_tasks(self) -> list[Task]:
        tasks = []
        try:
            response = self.table.scan()
            tasks.extend([Task(**item) for item in response.get("Items", [])])
            while "LastEvaluatedKey" in response:
                response = self.table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
                tasks.extend([Task(**item) for item in response.get("Items", [])])
            return tasks
        except EndpointConnectionError as e:
            logger.error("Failed to connect to DynamoDB endpoint.")
            raise DataAccessError("Failed to connect to DynamoDB endpoint.") from e
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ProvisionedThroughputExceededException":
                logger.error("DynamoDB throughput limit exceeded.")
                raise DataAccessError("DynamoDB throughput limit exceeded.") from e
            logger.error(f"Failed to list tasks: {e}")
            raise DataAccessError(f"Failed to list tasks: {e}") from e

    def create_task(self, task: Task) -> Task:
        if not task.id:  # 例: パーティションキーが必須の場合
            logger.error("Task ID is required.")
            raise InvalidParameterError("Task ID", task.id, "Task ID is required.")
        try:
            self.table.put_item(Item=task.dict())
            return task
        except ClientError as e:
            logger.error(f"Failed to create task: {e}")
            raise DataAccessError(f"Failed to create task: {e}") from e

    def delete_task(self, task_id: str) -> None:
        """
        指定されたタスクIDのタスクを削除します。

        :param task_id: 削除するタスクのID
        :raises InvalidParameterError: タスクIDが無効な場合
        :raises DataNotFoundError: 指定されたタスクが存在しない場合
        :raises DataAccessError: DynamoDBへのアクセスに失敗した場合
        """
        if not task_id:
            logger.error("Task ID is required for deletion.")
            raise InvalidParameterError("Task ID", task_id, "Task ID is required for deletion.")
        try:
            response = self.table.delete_item(
                Key={"id": task_id},
                ConditionExpression="attribute_exists(id)",  # タスクが存在する場合のみ削除
            )
            if response.get("Attributes") is None:
                logger.error(f"Task with ID {task_id} not found.")
                raise DataNotFoundError(f"Task with ID {task_id} not found.")
        except ClientError as e:
            logger.error(f"Failed to delete task with ID {task_id}: {e}")
            raise DataAccessError(f"Failed to delete task with ID {task_id}: {e}") from e

    def update_task(self, task_id: str, updated_task: Task) -> Task:
        """
        指定されたタスクIDのタスクを更新します。

        :param task_id: 更新するタスクのID
        :param updated_task: 更新後のタスクデータ
        :return: 更新されたタスク
        :raises InvalidParameterError: タスクIDまたは更新データが無効な場合
        :raises DataNotFoundError: 指定されたタスクが存在しない場合
        :raises DataAccessError: DynamoDBへのアクセスに失敗した場合
        """
        if not task_id:
            logger.error("Task ID is required for update.")
            raise InvalidParameterError("Task ID", task_id, "Task ID is required for update.")
        if not updated_task:
            logger.error("Updated task data is required.")
            raise InvalidParameterError("Updated Task", updated_task, "Updated task data is required.")
        try:
            response = self.table.update_item(
                Key={"id": task_id},
                UpdateExpression="SET #name = :name, #description = :description",
                ExpressionAttributeNames={"#name": "name", "#description": "description"},
                ExpressionAttributeValues={":name": updated_task.name, ":description": updated_task.description},
                ConditionExpression="attribute_exists(id)",  # タスクが存在する場合のみ更新
                ReturnValues="ALL_NEW",
            )
            attributes = response.get("Attributes")
            if not attributes:
                logger.error(f"Task with ID {task_id} not found.")
                raise DataNotFoundError(f"Task with ID {task_id} not found.")
            return Task(**attributes)
        except ClientError as e:
            logger.error(f"Failed to update task with ID {task_id}: {e}")
            raise DataAccessError(f"Failed to update task with ID {task_id}: {e}") from e

    def get_task(self, task_id: str) -> Task:
        """
        指定されたタスクIDのタスクを取得します。

        :param task_id: 取得するタスクのID
        :return: 取得したタスク
        :raises InvalidParameterError: タスクIDが無効な場合
        :raises DataNotFoundError: 指定されたタスクが存在しない場合
        :raises DataAccessError: DynamoDBへのアクセスに失敗した場合
        """
        if not task_id:
            logger.error("Task ID is required for retrieval.")
            raise InvalidParameterError("Task ID", task_id, "Task ID is required for retrieval.")
        try:
            response = self.table.get_item(Key={"id": task_id})
            item = response.get("Item")
            if not item:
                logger.error(f"Task with ID {task_id} not found.")
                raise DataNotFoundError(f"Task with ID {task_id} not found.")
            return Task(**item)
        except ClientError as e:
            logger.error(f"Failed to retrieve task with ID {task_id}: {e}")
            raise DataAccessError(f"Failed to retrieve task with ID {task_id}: {e}") from e
