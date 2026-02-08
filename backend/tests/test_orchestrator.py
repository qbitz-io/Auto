import unittest
from backend.agents.orchestrator import OrchestratorAgent

class TestOrchestratorAgent(unittest.TestCase):
    def setUp(self):
        self.orchestrator = OrchestratorAgent()

    def test_orchestrate(self):
        goal = "Test orchestration"
        result = self.orchestrator.orchestrate(goal)
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
