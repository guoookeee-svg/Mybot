import pytest
from mybot import Agent, Orchestrator, MockLLMClient


def test_orchestrator_register():
    orch = Orchestrator()
    agent = Agent(name="TestAgent")
    orch.register_agent(agent)
    assert orch.get_agent("TestAgent") is not None


def test_orchestrator_route():
    orch = Orchestrator()
    agent = Agent(name="RouterAgent", llm_client=MockLLMClient(["Routed response"]))
    orch.register_agent(agent)

    result = orch.route("Hello", strategy="auto")
    assert result["success"] is True
    assert result["agent"] == "RouterAgent"


def test_orchestrator_broadcast():
    orch = Orchestrator()
    agent1 = Agent(name="Agent1", llm_client=MockLLMClient(["Response 1"]))
    agent2 = Agent(name="Agent2", llm_client=MockLLMClient(["Response 2"]))
    orch.register_agent(agent1)
    orch.register_agent(agent2)

    result = orch.route("Hello", strategy="broadcast")
    assert result["success"] is True
    assert len(result["results"]) == 2


def test_orchestrator_collaboration():
    orch = Orchestrator()
    agent1 = Agent(name="A1", llm_client=MockLLMClient(["View 1"]))
    agent2 = Agent(name="A2", llm_client=MockLLMClient(["View 2", "Synthesis"]))
    orch.register_agent(agent1)
    orch.register_agent(agent2)

    result = orch.multi_agent_collaboration(
        "Topic",
        agent_names=["A1", "A2"],
        collaboration_mode="debate",
    )
    assert result["success"] is True
    assert len(result["perspectives"]) == 2


def test_orchestrator_pipeline():
    orch = Orchestrator()
    agent1 = Agent(name="P1", llm_client=MockLLMClient(["Step 1 output"]))
    agent2 = Agent(name="P2", llm_client=MockLLMClient(["Step 2 output"]))
    orch.register_agent(agent1)
    orch.register_agent(agent2)

    result = orch.multi_agent_collaboration(
        "Input",
        agent_names=["P1", "P2"],
        collaboration_mode="pipeline",
    )
    assert result["success"] is True
    assert len(result["steps"]) == 2
    assert result["final_output"] == "Step 2 output"
