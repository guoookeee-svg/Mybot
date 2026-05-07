import pytest
from mybot import Agent, tool, MockLLMClient


def test_agent_creation():
    agent = Agent(name="TestAgent", description="A test agent")
    assert agent.name == "TestAgent"
    assert agent.description == "A test agent"


def test_agent_run():
    agent = Agent(
        name="TestAgent",
        llm_client=MockLLMClient(["Hello! How can I help you?"]),
    )
    result = agent.run("Hi")
    assert "response" in result
    assert result["response"] == "Hello! How can I help you?"


def test_agent_with_tool():
    @tool(name="echo", description="Echo the input")
    def echo(message: str) -> str:
        return message

    agent = Agent(
        name="ToolAgent",
        llm_client=MockLLMClient(),
    )
    agent.register_tool(echo)

    assert len(agent.tool_registry.list_tools()) == 1
    assert agent.tool_registry.get("echo") is not None


def test_agent_session():
    agent = Agent(name="SessionAgent")
    session = agent.create_session()
    assert session.session_id is not None
    assert session.session_id in agent.sessions


def test_agent_history():
    agent = Agent(
        name="HistoryAgent",
        llm_client=MockLLMClient(["Response 1", "Response 2"]),
    )
    agent.run("Message 1")
    agent.run("Message 2")

    history = agent.get_history()
    assert len(history) >= 4


def test_agent_clear_memory():
    agent = Agent(name="ClearAgent")
    agent.run("Hello")
    agent.clear_memory()
    assert len(agent.get_history()) == 0
