import unittest
from backend.agents.orchestrator import OrchestratorAgent

class TestOrchestratorAgent(unittest.TestCase):
    def setUp(self):
        self.orchestrator = OrchestratorAgent()

    def test_orchestrate(self):
        goal = "Test orchestration"
        result = self.orchestrator.orchestrate(goal)
        self.assertIsNotNone(result)

    def test_orchestrate_empty_goal(self):
        goal = ""
        result = self.orchestrator.orchestrate(goal)
        self.assertIsNone(result)

    def test_orchestrate_none_goal(self):
        goal = None
        with self.assertRaises(TypeError):
            self.orchestrator.orchestrate(goal)

if __name__ == '__main__':
    unittest.main()
