import unittest
import asyncio
from unittest.mock import patch

with patch('backend.core.config.Settings') as MockSettings:
    MockSettings.return_value.openai_api_key = 'test_key'
    from backend.agents.planner import PlannerAgent

class TestPlannerAgent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.planner = PlannerAgent()

    async def test_plan_goal(self):
        goal = "Build a new feature"
        plan = await self.planner.plan(goal)
        self.assertIsInstance(plan, dict)
        self.assertIn("output", plan)
        self.assertTrue(len(plan["output"]) > 0)

    async def test_plan_empty_goal(self):
        goal = ""
        plan = await self.planner.plan(goal)
        self.assertIsInstance(plan, dict)
        self.assertIn("output", plan)
        self.assertEqual(len(plan["output"]), 0)

    async def test_plan_none_goal(self):
        goal = None
        with self.assertRaises(TypeError):
            await self.planner.plan(goal)

if __name__ == '__main__':
    unittest.main()
