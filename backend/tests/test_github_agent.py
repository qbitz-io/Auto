import unittest
import tempfile
import os
import subprocess
from backend.agents.github_agent import GitHubAgent

class TestGitHubAgent(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory and initialize a git repo
        self.test_dir = tempfile.TemporaryDirectory()
        subprocess.run(["git", "init"], cwd=self.test_dir.name, check=True)
        # Create an initial commit
        with open(os.path.join(self.test_dir.name, "README.md"), "w") as f:
            f.write("# Test Repo")
        subprocess.run(["git", "add", "."], cwd=self.test_dir.name, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.test_dir.name, check=True)

        self.agent = GitHubAgent(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_commit_and_tag(self):
        # Modify a file
        file_path = os.path.join(self.test_dir.name, "file.txt")
        with open(file_path, "w") as f:
            f.write("Some content")

        # Commit and tag
        message = "Test commit"
        success = self.agent.commit_and_tag(message)
        self.assertTrue(success)

        # Check that the tag was created
        result = subprocess.run(["git", "tag"], cwd=self.test_dir.name, check=True, stdout=subprocess.PIPE, text=True)
        tags = result.stdout.strip().splitlines()
        self.assertTrue(len(tags) > 0)

if __name__ == "__main__":
    unittest.main()
