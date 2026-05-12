"""Integration test stubs for Phase A — verify ApiServerAdapter wires
EventStore correctly at connect/disconnect time.

These tests don't run a real aiohttp server; they only verify the
factory-and-lifecycle plumbing for _store.
"""
import pytest

pytest.importorskip("fakeredis")
pytest.importorskip("redis")

from gateway.platforms.redis_store import InMemoryStore, make_store_from_env


@pytest.mark.asyncio
async def test_make_store_returns_in_memory_when_no_redis_url(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    store = make_store_from_env()
    assert isinstance(store, InMemoryStore)
    n = await store.incr_concurrency()
    assert n == 1
    await store.close()
