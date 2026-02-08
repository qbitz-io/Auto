import subprocess
import uuid
import os
import signal
import time
from typing import Dict, Optional

class SandboxInstance:
    def __init__(self, instance_id: str, process: subprocess.Popen):
        self.instance_id = instance_id
        self.process = process
        self.start_time = time.time()

    def is_running(self) -> bool:
        return self.process.poll() is None

    def terminate(self):
        if self.is_running():
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()

class SandboxGarage:
    def __init__(self):
        self.instances: Dict[str, SandboxInstance] = {}

    def spawn_instance(self, image: str = "flyio/clone:latest", command: Optional[str] = None) -> str:
        """
        Spawn a new isolated Fly.io clone instance using Docker.

        Args:
            image: Docker image to use for the instance.
            command: Optional command to run inside the container.

        Returns:
            instance_id: Unique ID of the spawned instance.
        """
        instance_id = str(uuid.uuid4())
        docker_command = ["docker", "run", "--rm", "--name", instance_id, "-d"]
        if command:
            docker_command.append(image)
            docker_command.extend(command.split())
        else:
            docker_command.append(image)

        try:
            # Run docker container detached
            result = subprocess.run(docker_command, capture_output=True, text=True, check=True)
            container_id = result.stdout.strip()
            # Store instance with dummy process handle (None) since we use docker CLI
            # We will track container by instance_id (container name)
            self.instances[instance_id] = SandboxInstance(instance_id, None)
            return instance_id
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to spawn instance: {e.stderr}")

    def is_instance_running(self, instance_id: str) -> bool:
        """Check if the docker container with instance_id is running."""
        try:
            result = subprocess.run(["docker", "ps", "-q", "-f", f"name={instance_id}"], capture_output=True, text=True, check=True)
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False

    def terminate_instance(self, instance_id: str) -> bool:
        """Terminate the docker container with instance_id."""
        try:
            subprocess.run(["docker", "stop", instance_id], capture_output=True, text=True, check=True)
            if instance_id in self.instances:
                del self.instances[instance_id]
            return True
        except subprocess.CalledProcessError:
            return False

    def list_instances(self) -> Dict[str, bool]:
        """List all managed instances and their running status."""
        status = {}
        for instance_id in list(self.instances.keys()):
            running = self.is_instance_running(instance_id)
            status[instance_id] = running
            if not running:
                del self.instances[instance_id]
        return status

    def cleanup(self):
        """Terminate all running instances."""
        for instance_id in list(self.instances.keys()):
            self.terminate_instance(instance_id)


# Singleton instance for global use
sandbox_garage = SandboxGarage()
