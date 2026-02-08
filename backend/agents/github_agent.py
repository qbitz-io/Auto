import subprocess
import os
import datetime

class GitHubAgent:
    """Handles GitHub commits, tagging, and pushing."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def commit_and_tag(self, message: str, tag: str) -> bool:
        try:
            # git add .
            subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)

            # git commit -m message
            subprocess.run(["git", "commit", "-m", message], cwd=self.repo_path, check=True)

            # git tag tag
            subprocess.run(["git", "tag", tag], cwd=self.repo_path, check=True)

            # git push
            subprocess.run(["git", "push"], cwd=self.repo_path, check=True)

            # git push --tags
            subprocess.run(["git", "push", "--tags"], cwd=self.repo_path, check=True)

            return True
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}")
            return False

# Initialize with project root
import pathlib
repo_path = pathlib.Path(__file__).parent.parent.resolve()
github_agent = GitHubAgent(str(repo_path))
