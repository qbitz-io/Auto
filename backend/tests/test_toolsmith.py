import unittest
from backend.agents.toolsmith import ToolsmithAgent
import os

class TestToolsmithAgent(unittest.TestCase):
    def setUp(self):
        self.toolsmith = ToolsmithAgent()
        self.tool_name = "example_tool"
        self.tool_code = "def example():\n    return 'example'"
        self.tool_path = f"backend/tools/{self.tool_name}.py"

    def tearDown(self):
        if os.path.exists(self.tool_path):
            os.remove(self.tool_path)

    def test_create_tool(self):
        result = self.toolsmith.create_tool(self.tool_name, self.tool_code)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.tool_path))

    def test_create_tool_empty_code(self):
        result = self.toolsmith.create_tool(self.tool_name, "")
        self.assertFalse(result)

    def test_create_tool_invalid_name(self):
        invalid_name = "../invalid"
        result = self.toolsmith.create_tool(invalid_name, self.tool_code)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
