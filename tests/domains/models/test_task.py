from src.domains.models.task import Task, TaskPriority, TaskStatus


def test_task_creation():
    task = Task.create(title="Test Task", description="This is a test task.", due_date="2023-12-31", priority="HIGH")

    assert task.title == "Test Task"
    assert task.description == "This is a test task."
    assert task.due_date == "2023-12-31"
    assert task.status.value == "TODO"
    assert task.priority.value == "HIGH"  # Assuming PRIORITY_DICT maps "HIGH" to TaskPriority.HIGH


def test_task_update():
    original_task = Task.create(
        title="Original Task", description="This is the original task.", due_date="2023-12-31", priority="MEDIUM"
    )

    updated_task = Task(
        id=original_task.id,  # Use the same ID to update the existing task
        title="Updated Task",
        description="This is the updated task.",
        priority=TaskPriority.HIGH,
    )

    updated = original_task.update(updated_task)

    assert updated.title == "Updated Task"
    assert updated.description == "This is the updated task."
    assert updated.due_date == "2023-12-31"  # remains unchanged
    assert updated.status == "TODO"  # remains unchanged
    assert updated.priority == "HIGH"  # Changed
