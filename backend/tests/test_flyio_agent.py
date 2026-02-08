import asyncio
import pytest
from backend.agents.flyio_agent import FlyioAgent

@pytest.mark.asyncio
async def test_spawn_and_list_instances():
    agent = FlyioAgent()
    instance_id = await agent.spawn_instance("main", "https://github.com/example/repo.git")
    assert instance_id in agent.instances
    instances = agent.list_instances()
    assert instance_id in instances

@pytest.mark.asyncio
async def test_health_check_and_cleanup(monkeypatch):
    agent = FlyioAgent()
    instance_id = "test-instance"
    agent.instances[instance_id] = {
        "app_name": "flyapp-test",
        "branch": "main",
        "repo_url": "https://github.com/example/repo.git",
        "status": "running",
        "url": "http://localhost"
    }

    # Patch httpx.AsyncClient.get to simulate 200 response
    class DummyResponse:
        status_code = 200

    class DummyClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
        async def get(self, url):
            return DummyResponse()

    monkeypatch.setattr("httpx.AsyncClient", lambda *args, **kwargs: DummyClient())

    healthy = await agent.health_check(instance_id)
    assert healthy is True

    # Patch subprocess.run to simulate successful cleanup
    def dummy_run(*args, **kwargs):
        return

    monkeypatch.setattr("subprocess.run", dummy_run)

    cleaned = await agent.cleanup_old_instance(instance_id)
    assert cleaned is True
    assert instance_id not in agent.instances

@pytest.mark.asyncio
async def test_switch_dns():
    agent = FlyioAgent()
    instance_id = "test-instance"
    agent.instances[instance_id] = {
        "app_name": "flyapp-test",
        "branch": "main",
        "repo_url": "https://github.com/example/repo.git",
        "status": "running",
        "url": "http://localhost"
    }

    switched = await agent.switch_dns(instance_id)
    assert switched is True
