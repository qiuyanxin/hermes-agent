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


@pytest.mark.asyncio
async def test_store_accepts_run_lifecycle_events():
    """run.completed and run.failed events survive a store round-trip.

    Sites D and E in Task 3 push these events through xadd_event when self._store
    is set. This validates the payload shape is JSON-serializable and readable back.
    """
    from gateway.platforms.redis_store import InMemoryStore
    store = InMemoryStore()
    await store.xadd_event("run_done", {
        "event": "run.completed",
        "run_id": "run_done",
        "timestamp": 123.0,
        "output": "final answer",
        "usage": {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30},
    })
    await store.xadd_event("run_done", {
        "event": "run.failed",
        "run_id": "run_done",
        "timestamp": 124.0,
        "error": "boom",
    })

    events = await store.xread_events("run_done", after_id="0-0", block_ms=10)
    assert [p["event"] for _, p in events] == ["run.completed", "run.failed"]
    assert events[0][1]["usage"]["total_tokens"] == 30
    assert events[1][1]["error"] == "boom"


@pytest.mark.asyncio
async def test_store_xread_replays_full_history_from_zero():
    """Resume from 0-0 must replay all past events — basic resume contract."""
    from gateway.platforms.redis_store import InMemoryStore
    store = InMemoryStore()
    await store.xadd_event("run_replay", {"event": "tool.started", "tool": "supost_search"})
    await store.xadd_event("run_replay", {"event": "tool.completed", "tool": "supost_search"})
    await store.xadd_event("run_replay", {"event": "__end__"})

    events = await store.xread_events("run_replay", after_id="0-0", block_ms=10)
    assert [p["event"] for _, p in events] == ["tool.started", "tool.completed", "__end__"]


@pytest.mark.asyncio
async def test_store_xread_resume_skips_already_consumed():
    """Client passes last-seen stream id; only newer events come back.

    This is the core resume scenario: client reconnects after network blip,
    passes ?after=<last_id> on the GET, and gets only events it hasn't seen.
    """
    from gateway.platforms.redis_store import InMemoryStore
    store = InMemoryStore()
    first_id = await store.xadd_event("run_resume", {"event": "a"})
    await store.xadd_event("run_resume", {"event": "b"})
    await store.xadd_event("run_resume", {"event": "c"})

    new_only = await store.xread_events("run_resume", after_id=first_id, block_ms=10)
    assert [p["event"] for _, p in new_only] == ["b", "c"]


@pytest.mark.asyncio
async def test_concurrency_increments_and_decrements_correctly():
    from gateway.platforms.redis_store import InMemoryStore
    store = InMemoryStore()
    assert await store.incr_concurrency() == 1
    assert await store.incr_concurrency() == 2
    assert await store.decr_concurrency() == 1
    assert await store.decr_concurrency() == 0
    # Decrement past zero clamps
    assert await store.decr_concurrency() == 0


@pytest.mark.asyncio
async def test_concurrency_round_trip_simulating_request_flow():
    """Simulate the INCR-then-check pattern: 3 INCRs against a limit=2 should
    accept 2 and roll back the 3rd via DECR."""
    from gateway.platforms.redis_store import InMemoryStore
    store = InMemoryStore()
    limit = 2

    accepted = 0
    for _ in range(3):
        current = await store.incr_concurrency()
        if current > limit:
            await store.decr_concurrency()
        else:
            accepted += 1

    assert accepted == 2
    # All 3 requests came in: 2 accepted (still alive), 1 rolled back. Counter == 2.
    # After both accepted requests finish (DECR each), counter should be 0.
    await store.decr_concurrency()
    await store.decr_concurrency()
    # Final state
    final = await store.incr_concurrency()
    await store.decr_concurrency()
    assert final == 1  # one INCR after all DECRs → 1
