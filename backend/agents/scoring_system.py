"""
SCORING SYSTEM agent that evaluates code on functionality, code quality, performance, and safety.
Produces a score from 0 to 10.
"""

import ast
import re

class ScoringSystemAgent:
    def __init__(self):
        pass

    def evaluate_code(self, code: str) -> float:
        """
        Evaluate the given code string and return a score from 0 to 10.

        Scoring criteria:
        - Functionality (4 points): Checks for presence of functions, classes, and basic syntax correctness.
        - Code Quality (2 points): Checks for docstrings, naming conventions, and line length.
        - Performance (2 points): Checks for obvious inefficiencies like nested loops or repeated computations.
        - Safety (2 points): Checks for use of unsafe functions and error handling.

        Args:
            code (str): The source code to evaluate.

        Returns:
            float: Score from 0 to 10.
        """
        functionality_score = self._score_functionality(code)
        quality_score = self._score_code_quality(code)
        performance_score = self._score_performance(code)
        safety_score = self._score_safety(code)

        total_score = functionality_score + quality_score + performance_score + safety_score
        return total_score

    def _score_functionality(self, code: str) -> float:
        # Check if code parses
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0.0

        # Check for presence of at least one function or class
        has_function = any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
        has_class = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))

        score = 0.0
        if has_function or has_class:
            score += 2.0
        else:
            score += 1.0  # some code but no functions/classes

        # Check for presence of return statements
        has_return = any(isinstance(node, ast.Return) for node in ast.walk(tree))
        if has_return:
            score += 2.0
        else:
            score += 1.0

        return min(score, 4.0)

    def _score_code_quality(self, code: str) -> float:
        lines = code.splitlines()
        score = 0.0

        # Check for docstrings in functions/classes
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0.0

        docstring_count = 0
        func_class_count = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                func_class_count += 1
                if ast.get_docstring(node):
                    docstring_count += 1

        if func_class_count > 0 and docstring_count / func_class_count >= 0.5:
            score += 1.0

        # Check for line length <= 79
        long_lines = sum(1 for line in lines if len(line) > 79)
        if long_lines / max(len(lines), 1) < 0.1:
            score += 1.0

        return min(score, 2.0)

    def _score_performance(self, code: str) -> float:
        # Simple heuristic: penalize nested loops > 2 levels
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0.0

        max_loop_depth = 0

        def loop_depth(node, current_depth=0):
            nonlocal max_loop_depth
            if isinstance(node, (ast.For, ast.While)):
                current_depth += 1
                max_loop_depth = max(max_loop_depth, current_depth)
            for child in ast.iter_child_nodes(node):
                loop_depth(child, current_depth)

        loop_depth(tree)

        if max_loop_depth > 2:
            return 0.5
        else:
            return 2.0

    def _score_safety(self, code: str) -> float:
        # Check for use of unsafe functions like eval, exec
        unsafe_patterns = [r'\beval\b', r'\bexec\b', r'\bos\.system\b', r'\bsubprocess\.Popen\b']
        unsafe_found = any(re.search(pattern, code) for pattern in unsafe_patterns)

        # Check for try-except blocks
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0.0

        has_try_except = any(isinstance(node, ast.Try) for node in ast.walk(tree))

        score = 0.0
        if not unsafe_found:
            score += 1.0
        if has_try_except:
            score += 1.0

        return min(score, 2.0)


# Example usage:
# agent = ScoringSystemAgent()
# score = agent.evaluate_code("""def foo():\n    return 42""")
# print(f"Score: {score}")
