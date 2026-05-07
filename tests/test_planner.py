import pytest
from mybot.planner import Planner, Task, TaskStatus


def test_create_task():
    planner = Planner()
    task = planner.create_task(name="test", description="A test task")
    assert task.name == "test"
    assert task.status == TaskStatus.PENDING
    assert task.task_id is not None


def test_task_dependencies():
    planner = Planner()
    task1 = planner.create_task(name="step1", description="First step")
    task2 = planner.create_task(
        name="step2",
        description="Second step",
        dependencies=[task1.task_id],
    )

    ready = planner.get_ready_tasks()
    assert len(ready) == 1
    assert ready[0].name == "step1"


def test_execute_task():
    planner = Planner()
    task = planner.create_task(name="simple", description="Simple task")

    def executor(t):
        return "done"

    result = planner.execute_task(task.task_id, executor)
    assert result.status == TaskStatus.COMPLETED
    assert result.result == "done"


def test_execute_all():
    planner = Planner()
    task1 = planner.create_task(name="a", description="Task A")
    task2 = planner.create_task(name="b", description="Task B")

    def executor(t):
        return f"completed {t.name}"

    completed = planner.execute_all(executor)
    assert len(completed) == 2
    assert all(t.status == TaskStatus.COMPLETED for t in completed)


def test_execution_history():
    planner = Planner()
    task = planner.create_task(name="hist", description="History test")

    def executor(t):
        return "result"

    planner.execute_task(task.task_id, executor)
    history = planner.get_execution_history()
    assert len(history) == 1
    assert history[0]["name"] == "hist"
