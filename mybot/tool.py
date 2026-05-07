import inspect
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, Union


@dataclass
class ToolParameter:
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }


class Tool(ABC):
    name: str = ""
    description: str = ""
    parameters: List[ToolParameter] = field(default_factory=list)

    def __init__(self):
        if not self.name:
            self.name = self.__class__.__name__

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        pass

    def to_openai_schema(self) -> Dict[str, Any]:
        properties = {}
        required = []
        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def validate_params(self, **kwargs) -> Optional[str]:
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                return f"Missing required parameter: {param.name}"
        return None


class FunctionTool(Tool):
    def __init__(self, func: Callable, name: Optional[str] = None, description: Optional[str] = None):
        self.func = func
        self.name = name or func.__name__
        self.description = description or (func.__doc__ or "")
        self.parameters = self._extract_parameters()
        super().__init__()

    def _extract_parameters(self) -> List[ToolParameter]:
        sig = inspect.signature(self.func)
        params = []
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list or getattr(param.annotation, "__origin__", None) == list:
                    param_type = "array"
                elif param.annotation == dict or getattr(param.annotation, "__origin__", None) == dict:
                    param_type = "object"

            required = param.default == inspect.Parameter.empty
            default = param.default if not required else None

            params.append(ToolParameter(
                name=name,
                type=param_type,
                description=f"Parameter {name}",
                required=required,
                default=default,
            ))
        return params

    def execute(self, **kwargs) -> ToolResult:
        error = self.validate_params(**kwargs)
        if error:
            return ToolResult(success=False, error=error)

        try:
            result = self.func(**kwargs)
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


def tool(name: Optional[str] = None, description: Optional[str] = None):
    def decorator(func: Callable) -> FunctionTool:
        return FunctionTool(func, name=name, description=description)
    return decorator


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        if name in self._tools:
            del self._tools[name]

    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())

    def execute(self, tool_name: str, **kwargs) -> ToolResult:
        tool = self.get(tool_name)
        if not tool:
            return ToolResult(success=False, error=f"Tool '{tool_name}' not found")
        return tool.execute(**kwargs)

    def to_openai_schemas(self) -> List[Dict[str, Any]]:
        return [tool.to_openai_schema() for tool in self._tools.values()]
