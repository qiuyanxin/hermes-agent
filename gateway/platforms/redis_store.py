# gateway/platforms/redis_store.py
"""Redis-backed event stream + concurrency counter for Hermes /v1/runs.

This is Phase A of the Hermes stateless migration (see ADR 0009).
It owns the persistent state previously held in ApiServerAdapter's
in-memory dicts:

  - run events queue (was self._run_streams[run_id]: asyncio.Queue)
  - global concurrency counter (was len(self._run_streams))

InMemoryStore is the no-Redis fallback for local development and tests;
RedisStore is the production path. ApiServerAdapter chooses one at
connect() time based on whether REDIS_URL is set.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

try:
    from redis import asyncio as aioredis  # type: ignore
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    aioredis = None  # type: ignore

STREAM_KEY_FMT = "hermes:run:{run_id}:stream"
STREAM_TTL_SECONDS = 600  # 10 min; matches existing _RUN_STREAM_TTL spirit
CONCURRENCY_KEY = "hermes:concurrency:current"
CONCURRENCY_TTL_SECONDS = 600  # safety net: counter expires if process dies mid-run
XREAD_MAX_COUNT = 100  # max events per XREAD call; client polls again for more


class EventStore(ABC):
    """Abstract interface. Both RedisStore and InMemoryStore conform."""

    @abstractmethod
    async def xadd_event(self, run_id: str, payload: Dict[str, Any]) -> str:
        ...

    @abstractmethod
    async def xread_events(
        self, run_id: str, after_id: str, block_ms: int
    ) -> List[Tuple[str, Dict[str, Any]]]:
        ...

    @abstractmethod
    async def incr_concurrency(self) -> int:
        ...

    @abstractmethod
    async def decr_concurrency(self) -> int:
        ...

    async def close(self) -> None:
        pass


class RedisStore(EventStore):
    """Production path. Backed by a real redis.asyncio.Redis client."""

    def __init__(self, client: "aioredis.Redis") -> None:
        self._r = client

    async def xadd_event(self, run_id: str, payload: Dict[str, Any]) -> str:
        key = STREAM_KEY_FMT.format(run_id=run_id)
        # Redis Streams field values are strings; JSON-encode complex payload.
        # Single field "data" holds the full event JSON to keep schema flexible.
        stream_id = await self._r.xadd(key, {"data": json.dumps(payload)})
        # EXPIRE every time is harmless and resets TTL on activity (desired).
        await self._r.expire(key, STREAM_TTL_SECONDS)
        return stream_id.decode() if isinstance(stream_id, bytes) else stream_id

    async def xread_events(
        self, run_id: str, after_id: str, block_ms: int
    ) -> List[Tuple[str, Dict[str, Any]]]:
        key = STREAM_KEY_FMT.format(run_id=run_id)
        # XREAD BLOCK returns None on timeout (no new events).
        resp = await self._r.xread({key: after_id}, block=block_ms, count=XREAD_MAX_COUNT)
        if not resp:
            return []
        # resp = [(stream_key, [(stream_id, {field: value}), ...])]
        _, entries = resp[0]
        out: List[Tuple[str, Dict[str, Any]]] = []
        for sid, fields in entries:
            sid_str = sid.decode() if isinstance(sid, bytes) else sid
            raw = fields.get(b"data") or fields.get("data") or b"{}"
            if isinstance(raw, bytes):
                raw = raw.decode()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("redis_store: malformed payload on %s id=%s", key, sid_str)
                continue
            out.append((sid_str, payload))
        return out

    async def incr_concurrency(self) -> int:
        n = await self._r.incr(CONCURRENCY_KEY)
        # Set/refresh TTL so a crashed process can't leak the counter forever.
        await self._r.expire(CONCURRENCY_KEY, CONCURRENCY_TTL_SECONDS)
        return int(n)

    async def decr_concurrency(self) -> int:
        n = await self._r.decr(CONCURRENCY_KEY)
        n = int(n)
        if n < 0:
            # Counter went negative (e.g., process restart lost INCR but caught DECR,
            # or a manual reset). Clamp to 0; concurrent racing DECRs all clamp to the
            # same 0, so the non-atomic read-modify-write is safe here.
            await self._r.set(CONCURRENCY_KEY, 0, ex=CONCURRENCY_TTL_SECONDS)
            return 0
        return n

    async def close(self) -> None:
        try:
            await self._r.aclose()
        except Exception as exc:  # pragma: no cover
            logger.debug("redis_store: aclose() raised during teardown: %s", exc)


class InMemoryStore(EventStore):
    """Fallback for local development and unit tests without Redis.

    NOT for production multi-replica use — provides per-process state only.
    """

    def __init__(self) -> None:
        self._streams: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
        self._lock = asyncio.Lock()
        self._counter = 0
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"{int(time.time() * 1000)}-{self._seq:010d}"

    async def xadd_event(self, run_id: str, payload: Dict[str, Any]) -> str:
        async with self._lock:
            sid = self._next_id()
            self._streams.setdefault(run_id, []).append((sid, payload))
            return sid

    async def xread_events(
        self, run_id: str, after_id: str, block_ms: int
    ) -> List[Tuple[str, Dict[str, Any]]]:
        # Simple non-blocking implementation: caller layer handles wait loop.
        async with self._lock:
            entries = self._streams.get(run_id, [])
            if after_id == "0-0":
                return list(entries)
            return [e for e in entries if e[0] > after_id]

    async def incr_concurrency(self) -> int:
        async with self._lock:
            self._counter += 1
            return self._counter

    async def decr_concurrency(self) -> int:
        async with self._lock:
            self._counter = max(0, self._counter - 1)
            return self._counter


def make_store_from_env() -> EventStore:
    """Factory: return RedisStore if REDIS_URL set + redis-py importable, else InMemoryStore."""
    url = os.environ.get("REDIS_URL")
    if url and REDIS_AVAILABLE:
        try:
            client = aioredis.from_url(url, decode_responses=False)
            logger.info("redis_store: using RedisStore (url=%s)", url.split("@")[-1])
            return RedisStore(client)
        except Exception as exc:
            logger.error(
                "redis_store: failed to init Redis (%s) — falling back to InMemoryStore", exc
            )
            return InMemoryStore()
    if not url:
        logger.info("redis_store: REDIS_URL not set — using InMemoryStore (single-process only)")
    else:
        logger.warning("redis_store: redis-py not importable — using InMemoryStore")
    return InMemoryStore()
