import pytest
from scripts.refresh import run_once, LAST_RUN_KEY

class FakeRedis:
    def __init__(self):
        self.store = {}

    def set(self, key, value, nx=False, ex=None):
        if nx and key in self.store:
            return None
        self.store[key] = value
        return True

    def delete(self, key):
        self.store.pop(key, None)

    def get(self, key):
        return self.store.get(key)

@pytest.mark.anyio
async def test_refresh_writes_last_run(monkeypatch):
    fake = FakeRedis()

    import scripts.refresh as refresh_mod
    monkeypatch.setattr(refresh_mod, "redis_client", fake)

    await run_once()

    assert fake.get(LAST_RUN_KEY) is not None