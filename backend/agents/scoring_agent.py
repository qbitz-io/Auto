import tempfile
import subprocess
import time
import os
import sys
import json

class ScoringAgent:
    """Evaluates code based on functionality, code quality, performance, and safety."""

    def score_code(self, code: str, test_results: dict = None) -> int:
        """Score code 0-10 based on criteria.

        Args:
            code: The source code string.
            test_results: Dict with test results.

        Returns:
            int: Score from 0 to 10.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            code_path = os.path.join(tmpdir, "code.py")
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Run code quality check (ruff) - use 'ruff check' instead of 'ruff'
            quality_score = self._run_ruff_check(code_path)

            # Run safety check (bandit)
            safety_score = self._run_bandit(code_path)

            # Run tests and measure performance
            functionality_score, performance_score = 0, 0
            if test_results:
                # Simplified: assume all_passed and performance_ok keys
                functionality_score = 4 if test_results.get("all_passed", False) else 0
                performance_score = 2 if test_results.get("performance_ok", False) else 0

            # Calculate total score
            # Functionality (4 pts), Code quality (2 pts), Performance (2 pts), Safety (2 pts)
            total_score = functionality_score + quality_score + performance_score + safety_score
            # Clamp score to 0-10
            total_score = max(0, min(10, total_score))

            return total_score

    def _run_ruff_check(self, code_path: str) -> int:
        """Run 'ruff check' linter and return code quality score (0-2)."""
        try:
            result = subprocess.run(["ruff", "check", code_path, "--exit-zero", "--format", "json"], capture_output=True, text=True)
            # Parse JSON output
            issues = json.loads(result.stdout) if result.stdout else []
            error_count = len(issues)
            # Score: 2 if no issues, 1 if <=5 issues, else 0
            if error_count == 0:
                return 2
            elif error_count <= 5:
                return 1
            else:
                return 0
        except Exception:
            return 0

    def _run_bandit(self, code_path: str) -> int:
        """Run bandit security scan and return safety score (0-2)."""
        try:
            result = subprocess.run(["bandit", "-r", code_path, "-f", "json"], capture_output=True, text=True)
            data = json.loads(result.stdout) if result.stdout else {}
            issues = data.get("results", [])
            # Count high and medium severity issues
            high_medium = [i for i in issues if i.get("issue_severity") in ("HIGH", "MEDIUM")]
            count = len(high_medium)
            # Score: 2 if no issues, 1 if <=2 issues, else 0
            if count == 0:
                return 2
            elif count <= 2:
                return 1
            else:
                return 0
        except Exception:
            return 0

scoring_agent = ScoringAgent()
