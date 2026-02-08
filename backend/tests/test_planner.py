import unittest
from backend.agents.planner import PlannerAgent

class TestPlannerAgent(unittest.TestCase):
    def setUp(self):
        self.planner = PlannerAgent()

    def test_plan_goal(self):
        goal = "Build a new feature"
        plan = self.planner.plan(goal)
        self.assertIsInstance(plan, list)
        self.assertTrue(len(plan) > 0)

if __name__ == '__main__':
    unittest.main()
