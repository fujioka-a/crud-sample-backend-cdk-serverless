import logging

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

from ..domains.interfaces.task_repository import ITaskRepository
from ..domains.models.task import Task
from ..exceptions.errors import DataAccessError, DataNotFoundError, InvalidParameterError

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class TaskDynamoDBRepository(ITaskRepository):
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

    def update_task(self, task_id: str, updates: dict) -> Task:
        """
        指定されたタスクIDのタスクを更新します。

        :param task_id: 更新するタスクのID
        :param updates: 更新するタスクの属性と値の辞書
        :return: 更新されたタスク
        :raises InvalidParameterError: タスクIDまたは更新データが無効な場合
        :raises DataNotFoundError: 指定されたタスクが存在しない場合
        :raises DataAccessError: DynamoDBへのアクセスに失敗した場合
        """
        if "id" in updates:
            raise InvalidParameterError("IDは更新できません。")

        update_expression = "SET " + ", ".join(f"{key} = :{key}" for key in updates.keys())
        expression_attribute_values = {f":{key}": value for key, value in updates.items()}

        response = self.table.update_item(
            Key={"id": task_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW",
        )

        if "Attributes" not in response:
            raise DataNotFoundError(f"Task ID {task_id} が見つかりません。")

        return Task(**response["Attributes"])

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
            self.table.delete_item(
                Key={"id": task_id},
                ConditionExpression="attribute_exists(id)",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.error(f"Task with ID {task_id} not found.")
                raise DataNotFoundError(f"Task with ID {task_id} not found.") from e

            logger.error(f"Failed to delete task with ID {task_id}: {e}")
            raise DataAccessError(f"Failed to delete task with ID {task_id}: {e}") from e
