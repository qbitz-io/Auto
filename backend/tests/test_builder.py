import unittest
from backend.agents.builder import BuilderAgent

class TestBuilderAgent(unittest.TestCase):
    def setUp(self):
        self.builder = BuilderAgent()

    def test_write_and_update_file(self):
        file_path = "backend/tests/temp_test_file.py"
        content = "print('Hello World')"
        self.builder.write_file(file_path, content)

        with open(file_path, 'r') as f:
            read_content = f.read()

        self.assertEqual(content, read_content)

        # Update file
        new_content = "print('Updated')"
        self.builder.write_file(file_path, new_content)

        with open(file_path, 'r') as f:
            updated_content = f.read()

        self.assertEqual(new_content, updated_content)

if __name__ == '__main__':
    unittest.main()
