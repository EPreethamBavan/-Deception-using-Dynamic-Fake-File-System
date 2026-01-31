import random
import os

class GitSkill:
    """
    Skill for simulating realistic Git operations.
    Can generate command sequences or (in future) actually perform them.
    """
    def __init__(self, username, home_dir):
        self.username = username
        self.home_dir = home_dir
        self.repos_dir = f"{home_dir}/repos"

    def generate_activity(self, context="coding"):
        """Generates a sequence of git commands based on context."""
        repo_name = random.choice(["backend-api", "frontend-app", "core-utils"])
        repo_path = f"{self.repos_dir}/{repo_name}"
        
        # Decide on activity type
        roll = random.random()
        
        if roll < 0.1:
            # Init new repo
            new_repo = f"experiment-{random.randint(100, 999)}"
            return self._init_repo(new_repo)
        elif roll < 0.6:
            # Standard commit loop
            return self._commit_loop(repo_path)
        else:
            # Inspection/Maintenance
            return self._inspection(repo_path)

    def _init_repo(self, repo_name):
        path = f"{self.repos_dir}/{repo_name}"
        return [
            f"mkdir -p {path}",
            f"cd {path}",
            "git init",
            f"echo '# {repo_name}' > README.md",
            "git add README.md",
            "git commit -m 'Initial commit'"
        ]

    def _commit_loop(self, repo_path):
        msgs = ["Fix typo", "Update logic", "Refactor module", "Add logging", "Bugfix"]
        files = ["main.py", "utils.py", "config.json", "README.md"]
        return [
            f"cd {repo_path}",
            "git status",
            f"touch {random.choice(files)}",
            "git add .",
            f"git commit -m '{random.choice(msgs)}'",
            "git push origin main"
        ]

    def _inspection(self, repo_path):
        return [
            f"cd {repo_path}",
            "git status",
            "git log -n 3",
            "git diff"
        ]
