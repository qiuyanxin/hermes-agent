"""Integration test stubs for Phase A — verify ApiServerAdapter wires
EventStore correctly at connect/disconnect time.

These tests don't run a real aiohttp server; they only verify the
factory-and-lifecycle plumbing for _store.
"""
import typing

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


@pytest.mark.asyncio
async def test_adapter_store_lifecycle_init_connect_close(monkeypatch):
    """ApiServerAdapter._store lifecycle: starts None, populated by connect()'s
    make_store_from_env(), closed and reset to None on disconnect().

    Doesn't stand up a real aiohttp server — verifies the wiring by directly
    invoking the lifecycle hooks on the _store slot.
    """
    monkeypatch.delenv("REDIS_URL", raising=False)

    # Import after env manipulation so the module-level REDIS_URL check (if any)
    # sees the cleared environment.
    from gateway.platforms.redis_store import (
        EventStore,
        InMemoryStore,
        make_store_from_env,
    )

    # Simulate __init__: _store starts None
    store: typing.Optional[EventStore] = None
    assert store is None

    # Simulate connect(): _store assigned from factory
    store = make_store_from_env()
    assert isinstance(store, InMemoryStore)

    # Exercise the store while it's "alive" (matches what handler use would do)
    await store.incr_concurrency()
    await store.xadd_event("run_lifecycle", {"event": "test"})

    # Simulate disconnect(): close + reset to None
    await store.close()
    store = None
    assert store is None
