import asyncio
import subprocess
import uuid
import httpx
import logging

logger = logging.getLogger(__name__)

class FlyioAgent:
    """Manages Fly.io instance deployment, health checks, DNS switching, and cleanup."""

    def __init__(self, org: str = None, region: str = None):
        self.instances = {}  # instance_id -> metadata
        self.org = org
        self.region = region

    async def spawn_instance(self, branch: str, repo_url: str) -> str:
        instance_id = str(uuid.uuid4())
        app_name = f"flyapp-{instance_id[:8]}"

        self.instances[instance_id] = {
            "app_name": app_name,
            "branch": branch,
            "repo_url": repo_url,
            "status": "deploying",
            "url": None,
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
            create_cmd = ["fly", "apps", "create", app_name]
            if self.org:
                create_cmd.extend(["--org", self.org])
            if self.region:
                create_cmd.extend(["--region", self.region])
            subprocess.run(create_cmd, check=True)

            # Clone repo and checkout branch
            subprocess.run(["git", "clone", repo_url, app_name], check=True)
            subprocess.run(["git", "checkout", branch], cwd=app_name, check=True)

            # Deploy to Fly
            subprocess.run(["fly", "deploy", "--app", app_name, "--remote-only"], cwd=app_name, check=True)

            # Get app info to find URL
            result = subprocess.run(["fly", "apps", "list"], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                if app_name in line:
                    # Example line: flyapp-12345678  running  https://flyapp-12345678.fly.dev
                    parts = line.split()
                    if len(parts) >= 3:
                        url = parts[2]
                        instance["url"] = url
                        break

            instance["status"] = "running"
            logger.info(f"Deployed Fly.io app {app_name} at {instance.get('url')}")
        except subprocess.CalledProcessError as e:
            instance["status"] = "failed"
            logger.error(f"Deployment failed for {app_name}: {e}")

    async def health_check(self, instance_id: str) -> bool:
        instance = self.instances.get(instance_id)
        if not instance or instance["status"] != "running" or not instance.get("url"):
            return False

        url = instance["url"]
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return True
        except Exception as e:
            logger.warning(f"Health check failed for {url}: {e}")
        return False

    async def switch_dns(self, instance_id: str) -> bool:
        instance = self.instances.get(instance_id)
        if not instance or instance["status"] != "running" or not instance.get("url"):
            return False

        # Placeholder for DNS switch logic
        # This could be implemented with DNS provider API calls
        # For now, we simulate success
        logger.info(f"Switching DNS to point to {instance['url']}")
        await asyncio.sleep(1)  # simulate delay
        return True

    async def cleanup_old_instance(self, instance_id: str) -> bool:
        instance = self.instances.get(instance_id)
        if not instance:
            return False
        app_name = instance["app_name"]
        try:
            subprocess.run(["fly", "apps", "destroy", app_name, "--yes"], check=True)
            del self.instances[instance_id]
            logger.info(f"Cleaned up Fly.io app {app_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Cleanup failed for {app_name}: {e}")
            return False

    def list_instances(self):
        return {iid: {"app_name": meta["app_name"], "status": meta["status"], "url": meta.get("url")} for iid, meta in self.instances.items()}

flyio_agent = FlyioAgent()
