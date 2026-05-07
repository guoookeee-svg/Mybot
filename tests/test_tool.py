import pytest
from mybot.tool import Tool, FunctionTool, ToolRegistry, tool, ToolResult


def test_function_tool():
    @tool(name="add", description="Add two numbers")
    def add(a: int, b: int) -> int:
        return a + b

    assert add.name == "add"
    assert add.description == "Add two numbers"

    result = add.execute(a=2, b=3)
    assert result.success is True
    assert result.data == 5


def test_tool_registry():
    registry = ToolRegistry()

    @tool()
    def hello(name: str) -> str:
        return f"Hello {name}"

    registry.register(hello)
    assert registry.get("hello") is not None

    result = registry.execute("hello", name="World")
    assert result.success is True
    assert result.data == "Hello World"


def test_tool_not_found():
    registry = ToolRegistry()
    result = registry.execute("nonexistent")
    assert result.success is False
    assert "not found" in result.error


def test_tool_schema():
    @tool(name="multiply", description="Multiply two numbers")
    def multiply(x: float, y: float) -> float:
        return x * y

    schema = multiply.to_openai_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "multiply"
    assert "x" in schema["function"]["parameters"]["properties"]
    assert "y" in schema["function"]["parameters"]["properties"]
