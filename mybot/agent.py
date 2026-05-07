import json
from typing import Any, Dict, Generator, List, Optional

from mybot.llm import LLMClient, MockLLMClient
from mybot.memory import Memory
from mybot.planner import Planner
from mybot.session import Session
from mybot.tool import Tool, ToolRegistry


class Agent:
    def __init__(
        self,
        name: str,
        description: str = "",
        system_prompt: Optional[str] = None,
        llm_client: Optional[LLMClient] = None,
        memory: Optional[Memory] = None,
        tools: Optional[List[Tool]] = None,
    ):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt or f"You are {name}, a helpful AI assistant."
        self.llm_client = llm_client or MockLLMClient()
        self.memory = memory or Memory()
        self.tool_registry = ToolRegistry()
        self.planner = Planner()
        self.sessions: Dict[str, Session] = {}

        if tools:
            for t in tools:
                self.tool_registry.register(t)

    def register_tool(self, tool: Tool) -> None:
        self.tool_registry.register(tool)

    def unregister_tool(self, name: str) -> None:
        self.tool_registry.unregister(name)

    def create_session(self, session_id: Optional[str] = None) -> Session:
        session = Session(session_id=session_id, memory=self.memory)
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)

    def run(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        use_tools: bool = True,
        max_iterations: int = 5,
    ) -> Dict[str, Any]:
        session = self.get_session(session_id) if session_id else None
        if not session and session_id:
            session = self.create_session(session_id)

        self.memory.add(prompt, role="user")

        messages = self.memory.to_messages()
        tools_schemas = self.tool_registry.to_openai_schemas() if use_tools else None

        iteration = 0
        tool_calls_history = []

        while iteration < max_iterations:
            iteration += 1

            response = self.llm_client.complete(
                messages=messages,
                system=self.system_prompt,
                tools=tools_schemas if tools_schemas else None,
            )

            content = response.get("content", "")
            tool_calls = response.get("tool_calls", [])
            finish_reason = response.get("finish_reason", "")

            if not tool_calls:
                self.memory.add(content, role="assistant")
                return {
                    "response": content,
                    "tool_calls": tool_calls_history,
                    "iterations": iteration,
                    "session_id": session.session_id if session else None,
                }

            self.memory.add(
                content or "[Tool call requested]",
                role="assistant",
                metadata={"tool_calls": tool_calls},
            )

            for tc in tool_calls:
                tool_name = tc["function"]["name"]
                try:
                    arguments = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    arguments = {}

                result = self.tool_registry.execute(tool_name, **arguments)

                tool_calls_history.append({
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": result.to_dict(),
                })

                result_content = json.dumps(result.to_dict(), ensure_ascii=False)
                self.memory.add(
                    result_content,
                    role="tool",
                    metadata={"tool_call_id": tc.get("id"), "tool_name": tool_name},
                )

            messages = self.memory.to_messages()

        final_response = self.llm_client.complete(
            messages=messages,
            system=self.system_prompt,
        )
        content = final_response.get("content", "")
        self.memory.add(content, role="assistant")

        return {
            "response": content,
            "tool_calls": tool_calls_history,
            "iterations": iteration,
            "session_id": session.session_id if session else None,
        }

    def stream(
        self,
        prompt: str,
        session_id: Optional[str] = None,
    ) -> Generator[str, None, None]:
        session = self.get_session(session_id) if session_id else None
        if not session and session_id:
            session = self.create_session(session_id)

        self.memory.add(prompt, role="user")
        messages = self.memory.to_messages()

        for chunk in self.llm_client.stream(
            messages=messages,
            system=self.system_prompt,
        ):
            yield chunk

        full_response = ""
        for chunk in self.llm_client.stream(
            messages=messages,
            system=self.system_prompt,
        ):
            full_response += chunk

        self.memory.add(full_response, role="assistant")

    def plan_and_execute(
        self,
        prompt: str,
        executor: Optional[Any] = None,
    ) -> Dict[str, Any]:
        tasks = self.planner.plan_from_prompt(prompt, llm_client=self.llm_client)

        if not executor:
            def default_executor(task):
                return self.run(task.description)["response"]
            executor = default_executor

        completed = self.planner.execute_all(executor)

        return {
            "tasks": [t.to_dict() for t in tasks],
            "completed": [t.to_dict() for t in completed],
            "total": len(tasks),
            "successful": len([t for t in completed if t.status.value == "completed"]),
        }

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return [entry.to_dict() for entry in self.memory.get_history(limit=limit)]

    def clear_memory(self) -> None:
        self.memory.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "tools": [t.name for t in self.tool_registry.list_tools()],
            "sessions": list(self.sessions.keys()),
        }
