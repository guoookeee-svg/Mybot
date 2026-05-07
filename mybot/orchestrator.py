from typing import Any, Dict, List, Optional

from mybot.agent import Agent


class Orchestrator:
    def __init__(self):
        self._agents: Dict[str, Agent] = {}

    def register_agent(self, agent: Agent) -> None:
        self._agents[agent.name] = agent

    def unregister_agent(self, name: str) -> None:
        if name in self._agents:
            del self._agents[name]

    def get_agent(self, name: str) -> Optional[Agent]:
        return self._agents.get(name)

    def list_agents(self) -> List[Agent]:
        return list(self._agents.values())

    def route(self, prompt: str, strategy: str = "auto") -> Dict[str, Any]:
        if strategy == "auto":
            agent = self._select_agent(prompt)
            if not agent:
                return {
                    "success": False,
                    "error": "No suitable agent found",
                    "response": None,
                }
            result = agent.run(prompt)
            return {
                "success": True,
                "agent": agent.name,
                "response": result["response"],
                "tool_calls": result.get("tool_calls", []),
            }

        elif strategy == "broadcast":
            results = []
            for agent in self._agents.values():
                result = agent.run(prompt)
                results.append({
                    "agent": agent.name,
                    "response": result["response"],
                })
            return {
                "success": True,
                "strategy": "broadcast",
                "results": results,
            }

        elif strategy == "sequential":
            results = []
            for agent in self._agents.values():
                result = agent.run(prompt)
                results.append({
                    "agent": agent.name,
                    "response": result["response"],
                })
                prompt = result["response"]
            return {
                "success": True,
                "strategy": "sequential",
                "results": results,
                "final_response": results[-1]["response"] if results else None,
            }

        else:
            return {
                "success": False,
                "error": f"Unknown strategy: {strategy}",
            }

    def _select_agent(self, prompt: str) -> Optional[Agent]:
        if not self._agents:
            return None

        if len(self._agents) == 1:
            return list(self._agents.values())[0]

        prompt_lower = prompt.lower()

        for name, agent in self._agents.items():
            desc_lower = agent.description.lower()
            if any(keyword in prompt_lower for keyword in desc_lower.split()[:3]):
                return agent

        for name, agent in self._agents.items():
            if any(tool.name.lower() in prompt_lower for tool in agent.tool_registry.list_tools()):
                return agent

        return list(self._agents.values())[0]

    def multi_agent_collaboration(
        self,
        prompt: str,
        agent_names: List[str],
        collaboration_mode: str = "debate",
    ) -> Dict[str, Any]:
        agents = [self._agents.get(name) for name in agent_names if name in self._agents]
        if not agents:
            return {"success": False, "error": "No valid agents specified"}

        if collaboration_mode == "debate":
            responses = []
            for agent in agents:
                result = agent.run(prompt)
                responses.append({
                    "agent": agent.name,
                    "response": result["response"],
                })

            synthesis_prompt = (
                f"Based on the following perspectives, provide a balanced synthesis:\n\n"
            )
            for r in responses:
                synthesis_prompt += f"{r['agent']}: {r['response']}\n\n"
            synthesis_prompt += "Synthesis:"

            synthesizer = agents[0]
            synthesis = synthesizer.run(synthesis_prompt)

            return {
                "success": True,
                "mode": "debate",
                "perspectives": responses,
                "synthesis": synthesis["response"],
            }

        elif collaboration_mode == "pipeline":
            current_output = prompt
            pipeline_results = []
            for agent in agents:
                result = agent.run(current_output)
                pipeline_results.append({
                    "agent": agent.name,
                    "input": current_output,
                    "output": result["response"],
                })
                current_output = result["response"]

            return {
                "success": True,
                "mode": "pipeline",
                "steps": pipeline_results,
                "final_output": current_output,
            }

        return {"success": False, "error": f"Unknown collaboration mode: {collaboration_mode}"}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agents": [agent.to_dict() for agent in self._agents.values()],
            "agent_count": len(self._agents),
        }
