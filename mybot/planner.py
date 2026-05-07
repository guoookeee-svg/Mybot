import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }


class Planner:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._execution_history: List[Dict[str, Any]] = []

    def create_task(
        self,
        name: str,
        description: str,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        task = Task(
            name=name,
            description=description,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )
        self._tasks[task.task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    def get_ready_tasks(self) -> List[Task]:
        ready = []
        for task in self._tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            deps_satisfied = all(
                self._tasks.get(dep_id) and self._tasks[dep_id].status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
            )
            if deps_satisfied:
                ready.append(task)
        return ready

    def execute_task(self, task_id: str, executor: Callable[[Task], Any]) -> Task:
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        if task.status != TaskStatus.PENDING:
            raise ValueError(f"Task {task_id} is not pending (status: {task.status.value})")

        task.status = TaskStatus.RUNNING
        try:
            result = executor(task)
            task.result = result
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            raise

        self._execution_history.append(task.to_dict())
        return task

    def execute_all(self, executor: Callable[[Task], Any]) -> List[Task]:
        completed = []
        while True:
            ready = self.get_ready_tasks()
            if not ready:
                break
            for task in ready:
                self.execute_task(task.task_id, executor)
                completed.append(task)
        return completed

    def reset(self) -> None:
        for task in self._tasks.values():
            if task.status in (TaskStatus.RUNNING, TaskStatus.FAILED):
                task.status = TaskStatus.PENDING
                task.result = None
                task.error = None

    def clear(self) -> None:
        self._tasks.clear()
        self._execution_history.clear()

    def get_execution_history(self) -> List[Dict[str, Any]]:
        return list(self._execution_history)

    def plan_from_prompt(self, prompt: str, llm_client=None) -> List[Task]:
        if not llm_client:
            task = self.create_task(
                name="direct_execution",
                description=prompt,
            )
            return [task]

        planning_prompt = (
            f"Given the following user request, break it down into a list of subtasks. "
            f"Each subtask should have a name and brief description. "
            f"Format as JSON array with objects containing 'name' and 'description' fields.\n\n"
            f"User request: {prompt}\n\n"
            f"Subtasks:"
        )

        response = llm_client.complete(planning_prompt, system="You are a task planner.")
        content = response.get("content", "")

        try:
            import json
            subtasks = json.loads(content)
            created = []
            prev_id = None
            for st in subtasks:
                deps = [prev_id] if prev_id else []
                task = self.create_task(
                    name=st["name"],
                    description=st["description"],
                    dependencies=deps,
                )
                created.append(task)
                prev_id = task.task_id
            return created
        except (json.JSONDecodeError, KeyError):
            task = self.create_task(
                name="direct_execution",
                description=prompt,
            )
            return [task]
