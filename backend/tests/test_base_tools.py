import unittest
import asyncio
import os
from unittest.mock import patch

with patch('backend.core.config.Settings') as MockSettings:
    MockSettings.return_value.openai_api_key = 'test_key'
    from backend.tools import base_tools
    from backend.core import settings

class TestBaseTools(unittest.IsolatedAsyncioTestCase):
    async def test_validate_file_path(self):
        # Valid path
        self.assertIsNone(base_tools._validate_file_path("backend/test.py"))
        # Invalid extension directory
        err = base_tools._validate_file_path("frontend/test.py")
        self.assertIsNotNone(err)
        # Windows reserved name
        err2 = base_tools._validate_file_path("backend/con.py")
        self.assertIsNotNone(err2)

    async def test_read_and_write_file(self):
        test_path = "backend/tests/temp_base_tool_test.py"
        content = "print('hello')"
        # Write file
        write_result = await base_tools.write_file(test_path, content)
        self.assertIn("Successfully wrote", write_result)
        # Read file
        read_result = await base_tools.read_file(test_path)
        self.assertEqual(read_result, content)
        # Cleanup
        if os.path.exists(settings.project_root / test_path):
            os.remove(settings.project_root / test_path)

    async def test_list_directory(self):
        result = await base_tools.list_directory("backend/tests")
        self.assertIn("FILE: test_base_tools.py", result)

    async def test_validate_python_syntax(self):
        valid_code = "def foo():\n    return 1"
        invalid_code = "def foo():\nreturn 1"
        valid_result = await base_tools.validate_python_syntax(valid_code)
        invalid_result = await base_tools.validate_python_syntax(invalid_code)
        self.assertIn("valid", valid_result)
        self.assertIn("Syntax error", invalid_result)

    async def test_run_command(self):
        # Simple command
        result = await base_tools.run_command("echo hello")
        self.assertIn("hello", result)
        # Command timeout
        result_timeout = await base_tools.run_command("sleep 35")
        self.assertIn("timed out", result_timeout)

    async def test_check_file_exists(self):
        test_path = "backend/tests/test_base_tools.py"
        exists = await base_tools.check_file_exists(test_path)
        self.assertEqual(exists, "exists")
        not_exists = await base_tools.check_file_exists("nonexistent.file")
        self.assertEqual(not_exists, "not found")

if __name__ == '__main__':
    unittest.main()
