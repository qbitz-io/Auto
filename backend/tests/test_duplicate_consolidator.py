import asyncio
import os
import pytest
from backend.agents.duplicate_consolidator import DuplicateConsolidatorAgent

@pytest.mark.asyncio
async def test_list_similar_files(tmp_path):
    # Create files with similar base names
    f1 = tmp_path / "module1.py"
    f2 = tmp_path / "module1_v2.py"
    f3 = tmp_path / "module2.py"
    f1.write_text("def foo(): pass")
    f2.write_text("def foo(): pass")
    f3.write_text("def bar(): pass")

    agent = DuplicateConsolidatorAgent()
    files = [str(f1), str(f2), str(f3)]
    similar = await agent._list_similar_files(files)
    assert (str(f1), str(f2)) in similar or (str(f2), str(f1)) in similar
    assert all(isinstance(pair, tuple) and len(pair) == 2 for pair in similar)

@pytest.mark.asyncio
async def test_compare_files(tmp_path):
    f1 = tmp_path / "file1.py"
    f2 = tmp_path / "file2.py"
    content1 = "def foo():\n    pass\n"
    content2 = "def foo():\n    print('hello')\n"
    f1.write_text(content1)
    f2.write_text(content2)

    agent = DuplicateConsolidatorAgent()
    result = await agent._compare_files(str(f1), str(f2))
    assert 'similarity' in result
    assert result['more_complete'] in (str(f1), str(f2))

@pytest.mark.asyncio
async def test_detect_and_consolidate(monkeypatch):
    # Setup dummy state with two similar files
    files = ["backend/agents/dummy1.py", "backend/agents/dummy1_v2.py"]

    # Patch state_manager.get_state to return dummy generated_files
    class DummyState:
        def __init__(self):
            self.generated_files = files.copy()
        async def save_state(self, state):
            pass

    dummy_state = DummyState()

    async def dummy_get_state():
        return dummy_state

    async def dummy_save_state(state):
        dummy_state.generated_files = state.generated_files

    monkeypatch.setattr("backend.core.state.state_manager.get_state", dummy_get_state)
    monkeypatch.setattr("backend.core.state.state_manager.save_state", dummy_save_state)

    # Patch read_file tool to return content
    async def dummy_arun(file_path):
        if file_path == files[0]:
            return "def foo():\n    pass\n"
        else:
            return "def foo():\n    print('hello')\n"

    agent = DuplicateConsolidatorAgent()
    for tool in agent.tools:
        if tool.name == "read_file":
            tool.arun = dummy_arun
        if tool.name == "write_file":
            async def dummy_write(file_path, content):
                # Simulate file removal by removing from dummy_state
                if file_path in dummy_state.generated_files:
                    dummy_state.generated_files.remove(file_path)
                return "Success"
            tool.arun = dummy_write

    result = await agent.detect_and_consolidate()
    assert result['duplicates_found'] == 1
    assert any("Removed duplicate file" in r for r in result['consolidation_results'])
