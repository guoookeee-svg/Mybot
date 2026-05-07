import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


@dataclass
class MemoryEntry:
    content: str
    role: str
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None
    entry_id: Optional[str] = None

    def __post_init__(self):
        if self.entry_id is None:
            self.entry_id = f"mem_{int(self.timestamp * 1000)}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp,
            "metadata": self.metadata or {},
        }


class StorageBackend(ABC):
    @abstractmethod
    def save(self, entry: MemoryEntry) -> None:
        pass

    @abstractmethod
    def load(self, limit: Optional[int] = None) -> List[MemoryEntry]:
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


class InMemoryStorage(StorageBackend):
    def __init__(self):
        self._entries: List[MemoryEntry] = []

    def save(self, entry: MemoryEntry) -> None:
        self._entries.append(entry)

    def load(self, limit: Optional[int] = None) -> List[MemoryEntry]:
        entries = sorted(self._entries, key=lambda e: e.timestamp)
        if limit:
            return entries[-limit:]
        return entries

    def search(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        query_lower = query.lower()
        matching = [
            e for e in self._entries
            if query_lower in e.content.lower()
        ]
        matching.sort(key=lambda e: e.timestamp, reverse=True)
        return matching[:limit]

    def clear(self) -> None:
        self._entries = []


class FileStorage(StorageBackend):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._entries: List[MemoryEntry] = []
        self._load_from_file()

    def _load_from_file(self) -> None:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._entries = [
                    MemoryEntry(
                        content=e["content"],
                        role=e["role"],
                        timestamp=e["timestamp"],
                        metadata=e.get("metadata"),
                        entry_id=e.get("entry_id"),
                    )
                    for e in data
                ]
        except (FileNotFoundError, json.JSONDecodeError):
            self._entries = []

    def _save_to_file(self) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in self._entries], f, ensure_ascii=False, indent=2)

    def save(self, entry: MemoryEntry) -> None:
        self._entries.append(entry)
        self._save_to_file()

    def load(self, limit: Optional[int] = None) -> List[MemoryEntry]:
        entries = sorted(self._entries, key=lambda e: e.timestamp)
        if limit:
            return entries[-limit:]
        return entries

    def search(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        query_lower = query.lower()
        matching = [
            e for e in self._entries
            if query_lower in e.content.lower()
        ]
        matching.sort(key=lambda e: e.timestamp, reverse=True)
        return matching[:limit]

    def clear(self) -> None:
        self._entries = []
        self._save_to_file()


class Memory:
    def __init__(self, storage: Optional[StorageBackend] = None, max_entries: int = 100):
        self.storage = storage or InMemoryStorage()
        self.max_entries = max_entries
        self._working_memory: List[MemoryEntry] = []

    def add(self, content: str, role: str = "user", metadata: Optional[Dict[str, Any]] = None) -> MemoryEntry:
        entry = MemoryEntry(
            content=content,
            role=role,
            timestamp=time.time(),
            metadata=metadata,
        )
        self.storage.save(entry)
        self._working_memory.append(entry)

        if len(self._working_memory) > self.max_entries:
            self._working_memory = self._working_memory[-self.max_entries:]

        return entry

    def get_history(self, limit: Optional[int] = None) -> List[MemoryEntry]:
        return self.storage.load(limit=limit)

    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        return self.get_history(limit=n)

    def search(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        return self.storage.search(query, limit=limit)

    def get_working_memory(self) -> List[MemoryEntry]:
        return self._working_memory

    def clear(self) -> None:
        self.storage.clear()
        self._working_memory = []

    def to_messages(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        entries = self.get_history(limit=limit)
        return [
            {"role": e.role, "content": e.content}
            for e in entries
        ]

    def summarize(self, llm_client=None) -> str:
        if not llm_client:
            return "[Memory summary not available without LLM]"

        messages = self.to_messages()
        if len(messages) <= 5:
            return "Conversation too short to summarize."

        prompt = (
            "Please summarize the following conversation in 2-3 sentences, "
            "highlighting key points and user intentions:\n\n"
        )
        for msg in messages:
            prompt += f"{msg['role']}: {msg['content']}\n"

        summary = llm_client.complete(prompt, system="You are a helpful summarizer.")
        return summary
