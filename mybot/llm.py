import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List, Optional, Union


class LLMClient(ABC):
    @abstractmethod
    def complete(
        self,
        messages: Union[str, List[Dict[str, str]]],
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def stream(
        self,
        messages: Union[str, List[Dict[str, str]]],
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Generator[str, None, None]:
        pass

    def _normalize_messages(self, messages: Union[str, List[Dict[str, str]]], system: Optional[str] = None) -> List[Dict[str, str]]:
        if isinstance(messages, str):
            msgs = [{"role": "user", "content": messages}]
        else:
            msgs = list(messages)

        if system:
            msgs.insert(0, {"role": "system", "content": system})

        return msgs


class OpenAIClient(LLMClient):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                raise ImportError("openai package is required. Install it with: pip install openai")
        return self._client

    def complete(
        self,
        messages: Union[str, List[Dict[str, str]]],
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        client = self._get_client()
        msgs = self._normalize_messages(messages, system)

        kwargs = {
            "model": self.model,
            "messages": msgs,
            "temperature": temperature,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = client.chat.completions.create(**kwargs)

        message = response.choices[0].message
        result = {
            "content": message.content or "",
            "role": message.role,
            "tool_calls": [],
            "finish_reason": response.choices[0].finish_reason,
        }

        if hasattr(message, "tool_calls") and message.tool_calls:
            for tc in message.tool_calls:
                result["tool_calls"].append({
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                })

        return result

    def stream(
        self,
        messages: Union[str, List[Dict[str, str]]],
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Generator[str, None, None]:
        client = self._get_client()
        msgs = self._normalize_messages(messages, system)

        kwargs = {
            "model": self.model,
            "messages": msgs,
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        response = client.chat.completions.create(**kwargs)

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class MockLLMClient(LLMClient):
    def __init__(self, responses: Optional[List[str]] = None):
        self.responses = responses or ["This is a mock response from the LLM."]
        self.call_count = 0

    def complete(
        self,
        messages: Union[str, List[Dict[str, str]]],
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        response_text = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1

        if tools and "weather" in str(messages).lower():
            return {
                "content": "",
                "role": "assistant",
                "tool_calls": [{
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": json.dumps({"location": "Beijing"}),
                    },
                }],
                "finish_reason": "tool_calls",
            }

        return {
            "content": response_text,
            "role": "assistant",
            "tool_calls": [],
            "finish_reason": "stop",
        }

    def stream(
        self,
        messages: Union[str, List[Dict[str, str]]],
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Generator[str, None, None]:
        response_text = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        words = response_text.split()
        for word in words:
            yield word + " "
