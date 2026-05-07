from mybot import Agent, tool


@tool(name="calculator", description="Perform basic math operations")
def calculator(expression: str) -> str:
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


@tool(name="greet", description="Greet a user by name")
def greet(name: str) -> str:
    return f"Hello, {name}! Welcome to MyBot."


def main():
    agent = Agent(
        name="MathAssistant",
        description="An agent that can do math and greet people",
        system_prompt="You are a helpful math assistant. Use tools when needed.",
    )

    agent.register_tool(calculator)
    agent.register_tool(greet)

    print("=== Basic Agent Demo ===\n")

    result1 = agent.run("What is 15 * 23 + 7?")
    print(f"User: What is 15 * 23 + 7?")
    print(f"Agent: {result1['response']}\n")

    result2 = agent.run("Please greet Alice")
    print(f"User: Please greet Alice")
    print(f"Agent: {result2['response']}\n")

    print("=== Conversation History ===")
    for entry in agent.get_history():
        print(f"[{entry['role']}] {entry['content'][:80]}...")


if __name__ == "__main__":
    main()
