import unittest
from backend.agents.validator import ValidatorAgent

class TestValidatorAgent(unittest.TestCase):
    def setUp(self):
        self.validator = ValidatorAgent()

    def test_validate_correct_code(self):
        code = """
        def add(a, b):
            return a + b
        """
        result = self.validator.validate_code(code)
        self.assertTrue(result['valid'])

    def test_validate_syntax_error(self):
        code = """
        def add(a, b):
        return a + b
        """
        result = self.validator.validate_code(code)
        self.assertFalse(result['valid'])
        self.assertIn('SyntaxError', result['error'])

if __name__ == '__main__':
    unittest.main()
