import logging

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

from ...domains.interfaces.task_repository import ITaskRepository
from ...domains.models.task import Task
from ...exceptions.errors import DataAccessError, DataNotFoundError, InvalidParameterError

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
            logger.exception("Failed to connect to DynamoDB endpoint.")
            raise DataAccessError("Failed to connect to DynamoDB endpoint.") from e
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ProvisionedThroughputExceededException":
                logger.exception("DynamoDB throughput limit exceeded.")
                raise DataAccessError("DynamoDB throughput limit exceeded.") from e
            logger.exception(f"Failed to list tasks: {e}")
            raise DataAccessError(f"Failed to list tasks: {e}") from e

    def create_task(self, task: Task):
        if not task.id:  # 例: パーティションキーが必須の場合
            logger.error("Task ID is required.")
            raise InvalidParameterError("Task ID", task.id, "Task ID is required.")
        try:
            inp = task.model_dump()
            inp["id"] = str(task.id)
            inp["status"] = task.status.value
            inp["priority"] = task.priority.value
            self.table.put_item(Item=inp)
        except ClientError as e:
            logger.exception(f"Failed to create task: {e}")
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
            logger.exception(f"Failed to retrieve task with ID {task_id}: {e}")
            raise DataAccessError(f"Failed to retrieve task with ID {task_id}: {e}") from e

    def update_task(self, updated_task: Task):
        """
        タスクを更新します。

        :param updated_task: 更新するタスク
        :return: 更新されたタスク
        :raises InvalidParameterError: タスクIDが無効な場合
        :raises DataNotFoundError: 指定されたタスクが存在しない場合
        :raises DataAccessError: DynamoDBへのアクセスに失敗した場合
        """
        if not updated_task.id:
            logger.error("Task ID is required for update.")
            raise InvalidParameterError("Task ID", updated_task.id, "Task ID is required for update.")
        try:
            inp = updated_task.model_dump()
            inp["id"] = str(updated_task.id)
            inp["status"] = updated_task.status.value
            inp["priority"] = updated_task.priority.value
            self.table.update_item(
                Key={"id": str(updated_task.id)},
                UpdateExpression=(
                    "SET #title = :title, #description = :description, "
                    "#due_date = :due_date, #status = :status, #priority = :priority"
                ),
                ExpressionAttributeNames={
                    "#title": "title",
                    "#description": "description",
                    "#due_date": "due_date",
                    "#status": "status",
                    "#priority": "priority",
                },
                ExpressionAttributeValues={
                    ":title": updated_task.title,
                    ":description": updated_task.description,
                    ":due_date": updated_task.due_date,
                    ":status": updated_task.status.value,
                    ":priority": updated_task.priority.value,
                },
                ConditionExpression="attribute_exists(id)",
            )
            return updated_task
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.exception(f"Task with ID {updated_task.id} not found.")
                raise DataNotFoundError(f"Task with ID {updated_task.id} not found.") from e

            logger.exception(f"Failed to update task with ID {updated_task.id}: {e}")
            raise DataAccessError(f"Failed to update task with ID {updated_task.id}: {e}") from e

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
                logger.exception(f"Task with ID {task_id} not found.")
                raise DataNotFoundError(f"Task with ID {task_id} not found.") from e

            logger.exception(f"Failed to delete task with ID {task_id}: {e}")
            raise DataAccessError(f"Failed to delete task with ID {task_id}: {e}") from e
