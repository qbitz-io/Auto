import unittest
import os
from backend.agents.builder import BuilderAgent

class TestBuilderAgent(unittest.TestCase):
    def setUp(self):
        self.builder = BuilderAgent()
        self.test_file = "backend/tests/temp_test_file.py"

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_write_and_update_file(self):
        content = "print('Hello World')"
        self.builder.write_file(self.test_file, content)

        with open(self.test_file, 'r') as f:
            read_content = f.read()

        self.assertEqual(content, read_content)

        # Update file
        new_content = "print('Updated')"
        self.builder.write_file(self.test_file, new_content)

        with open(self.test_file, 'r') as f:
            updated_content = f.read()

        self.assertEqual(new_content, updated_content)

    def test_write_file_invalid_path(self):
        invalid_path = "/invalid_path/test.py"
        content = "print('test')"
        with self.assertRaises(Exception):
            self.builder.write_file(invalid_path, content)

if __name__ == '__main__':
    unittest.main()
