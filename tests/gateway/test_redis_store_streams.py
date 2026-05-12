# tests/gateway/test_redis_store_streams.py
"""Unit tests for gateway.platforms.redis_store.

Uses fakeredis (already a transitive test dep) to validate XADD/XREAD semantics
without requiring a live Redis. If fakeredis is unavailable, tests are skipped
(this matches Hermes' existing test conventions — see tests/gateway/test_*.py).
"""
import asyncio
import pytest

pytest.importorskip("fakeredis")
pytest.importorskip("redis")

import fakeredis.aioredis  # type: ignore
from gateway.platforms.redis_store import (
    RedisStore,
    InMemoryStore,
    STREAM_KEY_FMT,
    CONCURRENCY_KEY,
    STREAM_TTL_SECONDS,
)


@pytest.mark.asyncio
async def test_xadd_then_xread_returns_event():
    fake = fakeredis.aioredis.FakeRedis()
    store = RedisStore(fake)

    await store.xadd_event("run_abc", {"event": "tool.started", "tool": "supost_search"})
    events = await store.xread_events("run_abc", after_id="0-0", block_ms=100)

    assert len(events) == 1
    stream_id, payload = events[0]
    assert payload["event"] == "tool.started"
    assert payload["tool"] == "supost_search"


@pytest.mark.asyncio
async def test_xread_with_after_id_skips_old_events():
    fake = fakeredis.aioredis.FakeRedis()
    store = RedisStore(fake)

    await store.xadd_event("run_abc", {"event": "a"})
    first = await store.xread_events("run_abc", after_id="0-0", block_ms=50)
    after_first = first[0][0]

    await store.xadd_event("run_abc", {"event": "b"})
    second = await store.xread_events("run_abc", after_id=after_first, block_ms=50)

    assert len(second) == 1
    assert second[0][1]["event"] == "b"


@pytest.mark.asyncio
async def test_xadd_sets_ttl():
    fake = fakeredis.aioredis.FakeRedis()
    store = RedisStore(fake)

    await store.xadd_event("run_ttl", {"event": "x"})
    ttl = await fake.ttl(STREAM_KEY_FMT.format(run_id="run_ttl"))

    assert 0 < ttl <= STREAM_TTL_SECONDS


@pytest.mark.asyncio
async def test_in_memory_store_round_trip():
    """InMemoryStore must satisfy the same interface for no-Redis test environments."""
    store = InMemoryStore()
    await store.xadd_event("run_mem", {"event": "delta", "delta": "hello"})
    events = await store.xread_events("run_mem", after_id="0-0", block_ms=10)
    assert events[0][1]["event"] == "delta"
    assert events[0][1]["delta"] == "hello"


@pytest.mark.asyncio
async def test_concurrency_incr_returns_new_count():
    fake = fakeredis.aioredis.FakeRedis()
    store = RedisStore(fake)

    n1 = await store.incr_concurrency()
    n2 = await store.incr_concurrency()
    n3 = await store.decr_concurrency()

    assert (n1, n2, n3) == (1, 2, 1)


@pytest.mark.asyncio
async def test_concurrency_decr_never_negative():
    """If a race causes DECR without prior INCR, counter must clamp to 0."""
    fake = fakeredis.aioredis.FakeRedis()
    store = RedisStore(fake)

    result = await store.decr_concurrency()
    # Either 0 (clamped) or -1 (raw) — store implementation must clamp
    assert result == 0
