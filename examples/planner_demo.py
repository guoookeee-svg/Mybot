from mybot import Agent, Planner, Task


def main():
    print("=== Planner Demo ===\n")

    planner = Planner()

    task1 = planner.create_task(
        name="research",
        description="Research the topic",
    )
    task2 = planner.create_task(
        name="outline",
        description="Create an outline",
        dependencies=[task1.task_id],
    )
    task3 = planner.create_task(
        name="write",
        description="Write the content",
        dependencies=[task2.task_id],
    )
    task4 = planner.create_task(
        name="review",
        description="Review and edit",
        dependencies=[task3.task_id],
    )

    print("Created tasks:")
    for task in planner.list_tasks():
        print(f"  - {task.name} ({task.task_id}): {task.description}")
        if task.dependencies:
            print(f"    Dependencies: {task.dependencies}")

    print("\nReady tasks (no pending dependencies):")
    ready = planner.get_ready_tasks()
    for task in ready:
        print(f"  - {task.name}")

    def mock_executor(task):
        print(f"  Executing: {task.name} - {task.description}")
        return f"Result of {task.name}"

    print("\nExecuting all tasks:")
    completed = planner.execute_all(mock_executor)

    print(f"\nCompleted {len(completed)} tasks")
    print("\nExecution history:")
    for entry in planner.get_execution_history():
        print(f"  - {entry['name']}: {entry['status']} -> {entry['result']}")

    print("\n=== Agent with Planner ===\n")

    agent = Agent(
        name="PlannerAgent",
        description="An agent that can plan and execute tasks",
    )

    result = agent.plan_and_execute("Write a blog post about AI agents")
    print(f"Planned {result['total']} tasks, completed {result['successful']}")
    for task in result["tasks"]:
        print(f"  - {task['name']}: {task['description']}")


if __name__ == "__main__":
    main()
