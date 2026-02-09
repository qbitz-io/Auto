import unittest
import asyncio
from backend.agents.validator import ValidatorAgent

class TestValidatorAgent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.validator = ValidatorAgent()

    async def test_validate_correct_code(self):
        code = """
        def add(a, b):
            return a + b
        """
        result = await self.validator.validate(code)
        self.assertTrue(result is not None)

    async def test_validate_syntax_error(self):
        code = """
        def add(a, b):
        return a + b
        """
        result = await self.validator.validate(code)
        self.assertTrue(result is not None)

    async def test_validate_empty_code(self):
        code = ""
        result = await self.validator.validate(code)
        self.assertTrue(result is not None)

    async def test_validate_none_code(self):
        # Expect TypeError for None input
        with self.assertRaises(TypeError):
            await self.validator.validate(None)

if __name__ == '__main__':
    unittest.main()
