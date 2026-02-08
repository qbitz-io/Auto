import asyncio
import subprocess
import uuid

class FlyioAgent:
    """Manages Fly.io instance deployment, health checks, DNS switching, and cleanup."""

    def __init__(self):
        self.instances = {}  # instance_id -> metadata

    async def spawn_instance(self, branch: str, repo_url: str) -> str:
        instance_id = str(uuid.uuid4())
        app_name = f"flyapp-{instance_id[:8]}"

        self.instances[instance_id] = {
            "app_name": app_name,
            "branch": branch,
            "repo_url": repo_url,
            "status": "deploying",
        }

        asyncio.create_task(self._deploy(instance_id))

        return instance_id

    async def _deploy(self, instance_id: str):
        instance = self.instances.get(instance_id)
        if not instance:
            return

        app_name = instance["app_name"]
        branch = instance["branch"]
        repo_url = instance["repo_url"]

        try:
            # Create Fly app
            subprocess.run(["fly", "apps", "create", app_name], check=True)

            # Clone repo and checkout branch
            subprocess.run(["git", "clone", repo_url, app_name], check=True)
            subprocess.run(["git", "checkout", branch], cwd=app_name, check=True)

            # Deploy to Fly
            subprocess.run(["fly", "deploy", "--app", app_name, "--remote-only"], cwd=app_name, check=True)

            self.instances[instance_id]["status"] = "running"
        except subprocess.CalledProcessError as e:
            self.instances[instance_id]["status"] = "failed"
            print(f"Deployment failed for {app_name}: {e}")

    async def health_check(self, instance_id: str) -> bool:
        instance = self.instances.get(instance_id)
        if not instance or instance["status"] != "running":
            return False
        # Implement real health check logic here
        # For example, curl the app URL and check response
        return True

    async def switch_dns(self, instance_id: str) -> bool:
        instance = self.instances.get(instance_id)
        if not instance or instance["status"] != "running":
            return False
        # Implement DNS switch logic here
        # For example, update DNS records to point to new instance
        return True

    async def cleanup_old_instance(self, instance_id: str) -> bool:
        instance = self.instances.get(instance_id)
        if not instance:
            return False
        app_name = instance["app_name"]
        try:
            subprocess.run(["fly", "apps", "destroy", app_name, "--yes"], check=True)
            del self.instances[instance_id]
            return True
        except subprocess.CalledProcessError as e:
            print(f"Cleanup failed for {app_name}: {e}")
            return False

flyio_agent = FlyioAgent()
