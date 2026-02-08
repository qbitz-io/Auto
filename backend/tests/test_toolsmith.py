import unittest
from backend.agents.toolsmith import ToolsmithAgent

class TestToolsmithAgent(unittest.TestCase):
    def setUp(self):
        self.toolsmith = ToolsmithAgent()

    def test_create_tool(self):
        tool_name = "example_tool"
        tool_code = "def example():\n    return 'example'"
        result = self.toolsmith.create_tool(tool_name, tool_code)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
