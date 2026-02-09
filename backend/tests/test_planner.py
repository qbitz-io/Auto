import unittest
from unittest.mock import patch

with patch('backend.core.config.Settings') as MockSettings:
    MockSettings.return_value.openai_api_key = 'test_key'
    from backend.agents.planner import PlannerAgent

class TestPlannerAgent(unittest.TestCase):
    def setUp(self):
        self.planner = PlannerAgent()

    def test_plan_goal(self):
        goal = "Build a new feature"
        plan = self.planner.plan(goal)
        self.assertIsInstance(plan, list)
        self.assertTrue(len(plan) > 0)

    def test_plan_empty_goal(self):
        goal = ""
        plan = self.planner.plan(goal)
        self.assertIsInstance(plan, list)
        self.assertEqual(len(plan), 0)

    def test_plan_none_goal(self):
        goal = None
        with self.assertRaises(TypeError):
            self.planner.plan(goal)

if __name__ == '__main__':
    unittest.main()
