import pytest
from mybot.memory import Memory, InMemoryStorage, FileStorage, MemoryEntry


def test_memory_add_and_retrieve():
    memory = Memory()
    entry = memory.add("Hello", role="user")
    assert entry.content == "Hello"
    assert entry.role == "user"

    history = memory.get_history()
    assert len(history) == 1
    assert history[0].content == "Hello"


def test_memory_search():
    memory = Memory()
    memory.add("I love Python programming", role="user")
    memory.add("JavaScript is also great", role="user")
    memory.add("Rust is fast", role="user")

    results = memory.search("Python")
    assert len(results) == 1
    assert "Python" in results[0].content


def test_memory_to_messages():
    memory = Memory()
    memory.add("Hello", role="user")
    memory.add("Hi there", role="assistant")

    messages = memory.to_messages()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


def test_memory_clear():
    memory = Memory()
    memory.add("Hello", role="user")
    memory.clear()
    assert len(memory.get_history()) == 0


def test_file_storage(tmp_path):
    filepath = tmp_path / "memory.json"
    storage = FileStorage(str(filepath))

    entry = MemoryEntry(content="Test", role="user", timestamp=1234567890.0)
    storage.save(entry)

    loaded = storage.load()
    assert len(loaded) == 1
    assert loaded[0].content == "Test"

    storage.clear()
    assert len(storage.load()) == 0
