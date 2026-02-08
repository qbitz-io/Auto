import subprocess
import os
import datetime
import re

class GitHubAgent:
    """Handles GitHub commits, tagging, and pushing."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_latest_tag(self) -> str:
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                cwd=self.repo_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            # No tags found
            return "0.0.0"

    def increment_version(self, version: str) -> str:
        # Simple semantic version increment: increment patch version
        match = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
        if not match:
            return "0.0.1"
        major, minor, patch = map(int, match.groups())
        patch += 1
        return f"{major}.{minor}.{patch}"

    def commit_and_tag(self, message: str) -> bool:
        try:
            # git add .
            subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)

            # git commit -m message
            subprocess.run(["git", "commit", "-m", message], cwd=self.repo_path, check=True)

            # Get latest tag
            latest_tag = self.get_latest_tag()
            new_tag = self.increment_version(latest_tag)

            # git tag new_tag
            subprocess.run(["git", "tag", new_tag], cwd=self.repo_path, check=True)

            # git push
            subprocess.run(["git", "push"], cwd=self.repo_path, check=True)

            # git push --tags
            subprocess.run(["git", "push", "--tags"], cwd=self.repo_path, check=True)

            print(f"Committed and tagged with {new_tag}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}")
            return False

# Initialize with project root
import pathlib
repo_path = pathlib.Path(__file__).parent.parent.resolve()
github_agent = GitHubAgent(str(repo_path))
