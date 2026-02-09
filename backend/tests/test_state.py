import unittest
import asyncio
from datetime import datetime, timedelta
from backend.core.state import StateManager, BuildStep, SystemCapability
import os
import tempfile
from unittest.mock import patch

with patch('backend.core.config.Settings') as MockSettings:
    MockSettings.return_value.openai_api_key = 'test_key'

class TestStateManager(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Use a temporary file for state
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.state_manager = StateManager(state_file=self.temp_file.name)

    async def asyncTearDown(self):
        self.temp_file.close()
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    async def test_load_and_save_state(self):
        state = await self.state_manager.load()
        self.assertIsNotNone(state)
        await self.state_manager.save()

    async def test_add_and_update_build_step(self):
        step = BuildStep(id="step1", agent="test_agent", action="test_action", status="pending")
        await self.state_manager.add_build_step(step)
        state = await self.state_manager.get_state()
        self.assertIn(step, state.build_steps)

        await self.state_manager.update_build_step("step1", "completed", result="success")
        state = await self.state_manager.get_state()
        updated_step = next((s for s in state.build_steps if s.id == "step1"), None)
        self.assertIsNotNone(updated_step)
        self.assertEqual(updated_step.status, "completed")
        self.assertEqual(updated_step.result, "success")

    async def test_add_and_update_capability(self):
        cap = SystemCapability(name="test_cap", description="desc", implemented=False)
        await self.state_manager.add_capability(cap)
        state = await self.state_manager.get_state()
        self.assertIn(cap, state.capabilities)

        await self.state_manager.update_capability("test_cap", True, file_path="path/to/file.py")
        state = await self.state_manager.get_state()
        updated_cap = next((c for c in state.capabilities if c.name == "test_cap"), None)
        self.assertIsNotNone(updated_cap)
        self.assertTrue(updated_cap.implemented)
        self.assertEqual(updated_cap.file_path, "path/to/file.py")

    async def test_add_generated_file_and_capability(self):
        file_path = "backend/tools/test_tool.py"
        await self.state_manager.add_generated_file(file_path)
        state = await self.state_manager.get_state()
        self.assertIn(file_path, state.generated_files)
        cap_name = file_path.replace('/', '_').replace('.', '_')
        cap = next((c for c in state.capabilities if c.name == cap_name), None)
        self.assertIsNotNone(cap)
        self.assertTrue(cap.implemented)

    async def test_cache_results(self):
        task_hash = "hash123"
        result = "result_data"
        await self.state_manager.add_cached_result(task_hash, result)
        cached = await self.state_manager.get_cached_result(task_hash)
        self.assertEqual(cached, result)

        # Simulate expired cache
        state = await self.state_manager.get_state()
        cache = state.metadata.get("task_cache", {})
        if task_hash in cache:
            cache[task_hash]["timestamp"] = (datetime.now() - timedelta(hours=2)).isoformat()
        await self.state_manager.save()

        expired = await self.state_manager.get_cached_result(task_hash)
        self.assertIsNone(expired)

if __name__ == '__main__':
    unittest.main()
