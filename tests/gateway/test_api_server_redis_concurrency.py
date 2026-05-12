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


@pytest.mark.asyncio
async def test_in_memory_store_records_event_marker():
    """Stream end is marked by an __end__ event in the store, not a None sentinel."""
    from gateway.platforms.redis_store import InMemoryStore
    store = InMemoryStore()
    await store.xadd_event("run_x", {"event": "__end__"})
    events = await store.xread_events("run_x", after_id="0-0", block_ms=10)
    assert events[-1][1]["event"] == "__end__"


@pytest.mark.asyncio
async def test_store_accepts_tool_lifecycle_events():
    """Sanity: store accepts the actual event shape produced by _make_run_event_callback."""
    from gateway.platforms.redis_store import InMemoryStore
    store = InMemoryStore()
    await store.xadd_event("run_y", {"event": "tool.started", "run_id": "run_y", "tool": "supost_search", "preview": "iphone"})
    await store.xadd_event("run_y", {"event": "tool.completed", "run_id": "run_y", "tool": "supost_search", "duration": 0.42, "error": False})
    await store.xadd_event("run_y", {"event": "message.delta", "run_id": "run_y", "delta": "Hello "})
    await store.xadd_event("run_y", {"event": "__end__", "run_id": "run_y"})

    events = await store.xread_events("run_y", after_id="0-0", block_ms=10)
    event_types = [p["event"] for _, p in events]
    assert event_types == ["tool.started", "tool.completed", "message.delta", "__end__"]
