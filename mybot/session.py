import uuid
from typing import Any, Dict, List, Optional

from mybot.memory import Memory
from mybot.tool import ToolRegistry


class Session:
    def __init__(self, session_id: Optional[str] = None, memory: Optional[Memory] = None):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.memory = memory or Memory()
        self.context: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}

    def add_message(self, content: str, role: str = "user", metadata: Optional[Dict[str, Any]] = None) -> None:
        self.memory.add(content, role=role, metadata=metadata)

    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        return self.memory.to_messages(limit=limit)

    def set_context(self, key: str, value: Any) -> None:
        self.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        return self.context.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "context": self.context,
            "metadata": self.metadata,
            "message_count": len(self.memory.get_history()),
        }
