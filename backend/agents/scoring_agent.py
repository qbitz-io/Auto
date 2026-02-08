class ScoringAgent:
    """Evaluates code based on functionality, code quality, performance, and safety."""

    def score_code(self, code: str, test_results: dict) -> int:
        """Score code 0-10 based on criteria.

        Args:
            code: The source code string.
            test_results: Dict with test outcomes and metrics.

        Returns:
            int: Score from 0 to 10.
        """
        score = 0

        # Functionality (4 pts): all tests pass
        if test_results.get("all_passed", False):
            score += 4

        # Code quality (2 pts): simple heuristics
        if self._check_code_quality(code):
            score += 2

        # Performance (2 pts): test_results may include performance metrics
        if test_results.get("performance_ok", False):
            score += 2

        # Safety (2 pts): check for unsafe patterns
        if self._check_safety(code):
            score += 2

        return score

    def _check_code_quality(self, code: str) -> bool:
        # Placeholder: check for PEP8 compliance, complexity, etc.
        # For now, accept all
        return True

    def _check_safety(self, code: str) -> bool:
        # Placeholder: check for dangerous imports or code
        # For now, accept all
        return True

scoring_agent = ScoringAgent()
