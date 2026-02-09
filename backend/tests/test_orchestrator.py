import unittest
import asyncio
from backend.agents.orchestrator import OrchestratorAgent

class TestOrchestratorAgent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.orchestrator = OrchestratorAgent()

    async def test_run(self):
        goal = "Test orchestration"
        result = await self.orchestrator.run(goal)
        self.assertIsNotNone(result)

    async def test_run_empty_goal(self):
        goal = ""
        result = await self.orchestrator.run(goal)
        self.assertIsNotNone(result)  # Should return some output even for empty

    async def test_run_none_goal(self):
        goal = None
        with self.assertRaises(TypeError):
            await self.orchestrator.run(goal)

if __name__ == '__main__':
    unittest.main()
