import unittest
import os
import asyncio
from backend.agents.builder import BuilderAgent

class TestBuilderAgent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.builder = BuilderAgent()
        self.test_file = "temp_test_file"

    async def asyncTearDown(self):
        # Remove the test file if exists
        import os
        file_path = f"backend/tests/{self.test_file}.py"
        if os.path.exists(file_path):
            os.remove(file_path)

    async def test_write_and_update_file(self):
        content = "print('Hello World')"
        file_path = await self.builder.write_file("python", self.test_file, content)

        with open(file_path, 'r') as f:
            read_content = f.read()

        self.assertEqual(content, read_content)

        # Update file
        new_content = "print('Updated')"
        file_path = await self.builder.write_file("python", self.test_file, new_content)

        with open(file_path, 'r') as f:
            updated_content = f.read()

        self.assertEqual(new_content, updated_content)

    async def test_write_file_invalid_language(self):
        with self.assertRaises(ValueError):
            await self.builder.write_file("invalidlang", self.test_file, "print('test')")

    async def test_write_file_empty_content(self):
        with self.assertRaises(ValueError):
            await self.builder.write_file("python", self.test_file, "")

if __name__ == '__main__':
    unittest.main()
