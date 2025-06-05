import logging

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

from ..exception.errors import DataAccessError, InvalidParameterError
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
