import boto3
from botocore.exceptions import ClientError

from ..schemas.task import Task


class TaskDynamoDBRepository:
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def list_tasks(self) -> list[Task]:
        try:
            response = self.table.scan()
            return [Task(**item) for item in response.get("Items", [])]
        except ClientError as e:
            raise RuntimeError(f"Failed to list tasks: {e}") from e

    def create_task(self, task: Task) -> Task:
        try:
            self.table.put_item(Item=task.dict())
            return task
        except ClientError as e:
            raise RuntimeError(f"Failed to create task: {e}") from e
