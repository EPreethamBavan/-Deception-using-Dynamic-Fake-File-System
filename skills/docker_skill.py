import random

class DockerSkill:
    """
    Skill for simulating realistic Docker operations.
    """
    def __init__(self, username, home_dir):
        self.username = username
        self.home_dir = home_dir

    def generate_activity(self, context="deploy"):
        """Generates a sequence of docker commands."""
        roll = random.random()
        
        if roll < 0.2:
            return self._cleanup()
        elif roll < 0.6:
            return self._build_run()
        else:
            return self._inspect()

    def _build_run(self):
        images = ["nginx:latest", "python:3.9-slim", "node:16-alpine", "postgres:13"]
        img = random.choice(images)
        container = f"test-{random.randint(1000,9999)}"
        return [
            "docker ps",
            f"docker pull {img}",
            f"docker run -d --name {container} {img}",
            f"docker logs {container}"
        ]

    def _cleanup(self):
        return [
            "docker ps -a",
            "docker system prune -f"
        ]
        
    def _inspect(self):
        return [
            "docker ps",
            "docker images",
            "docker stats --no-stream"
        ]
