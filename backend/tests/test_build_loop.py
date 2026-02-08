import unittest
from backend.agents.build_loop import BuildLoopAgent

class TestBuildLoopAgent(unittest.TestCase):
    def setUp(self):
        self.build_loop = BuildLoopAgent()

    def test_run_loop(self):
        result = self.build_loop.run_loop()
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
