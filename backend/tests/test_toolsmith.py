import unittest
import asyncio
import os
from backend.agents.toolsmith import ToolsmithAgent

class TestToolsmithAgent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.toolsmith = ToolsmithAgent()
        self.tool_name = "example_tool"
        self.tool_code = "def example():\n    return 'example'"
        self.tool_path = f"backend/tools/{self.tool_name}.py"

    async def asyncTearDown(self):
        if os.path.exists(self.tool_path):
            os.remove(self.tool_path)

    async def test_create_tool(self):
        # Test creating a valid tool
        result = await self.toolsmith.create_tool(self.tool_code)
        self.assertIsNotNone(result)

    async def test_create_tool_empty_code(self):
        # Expect ValueError for empty code
        with self.assertRaises(ValueError):
            await self.toolsmith.create_tool("")

    async def test_create_tool_none_code(self):
        # Expect TypeError for None code
        with self.assertRaises(TypeError):
            await self.toolsmith.create_tool(None)

if __name__ == '__main__':
    unittest.main()
