#!/usr/bin/env python3
"""SpringBrand request_human_handoff tool.

Routes the SUpost concierge's "operator hand-off" step back to the demo
agent-backend. The actual handoff has demo-side side effects (PG row in
demo's handoffs table, Lark interactive card via feishu-gateway, run
state transition to awaiting_handoff) that can't run inside Hermes —
this tool is a thin proxy that POSTs to demo's
``/v1/internal/handoff_dispatch`` and returns demo's response back to
the LLM.

Correlation: Hermes only knows ``session_id`` (the ``sb_<tenant>_<agent>_<thread>``
key created by demo's executeBuyerSupostViaHermes). Demo writes the active
run/thread/tenant context into Redis under ``hermes_handoff_ctx:<session_id>``
with a 10-minute TTL just before invoking Hermes. The HTTP endpoint reads
that hint to recover demo's run identifiers.

The Hermes runtime passes ``session_id`` as the ``task_id`` kwarg to tool
handlers (see api_server.py: ``task_id=session_id or "default"``).
"""
from __future__ import annotations

import json
import os
from typing import Any, List, Optional

import httpx

from tools.registry import registry


HANDOFF_TIMEOUT_SECONDS = 25.0


def _agent_backend_url() -> str:
    return (os.environ.get("AGENT_BACKEND_INTERNAL_URL") or "").rstrip("/")


def _agent_api_token() -> str:
    # Same shared service token agent-backend uses to authenticate
    # internal callers (feishu-gateway et al). Set it on the hermes-agent
    # service via Railway template ref ${{agent-backend.AGENT_API_TOKEN}}.
    return os.environ.get("AGENT_API_TOKEN", "")


def check_springbrand_handoff_requirements() -> bool:
    return bool(_agent_backend_url())


def springbrand_handoff(
    post_url: str,
    user_intent: str,
    selection_reason: str = "",
    suggested_questions: Optional[List[str]] = None,
    session_id: str = "",
) -> str:
    if not session_id:
        return json.dumps(
            {"ok": False, "error": "missing session_id (Hermes runtime did not propagate task_id)"},
            ensure_ascii=False,
        )
    base = _agent_backend_url()
    if not base:
        return json.dumps(
            {"ok": False, "error": "AGENT_BACKEND_INTERNAL_URL not configured on hermes-agent"},
            ensure_ascii=False,
        )

    # No X-Tenant-Id header: Hermes runs cross-tenant in a single process
    # and has no way to know the caller's tenant_id. demo's
    # /v1/internal/handoff_dispatch resolves tenant_id from the Redis
    # run-context keyed by session_id. The Bearer token authenticates the
    # service-to-service call; tenant scoping is handled server-side.
    headers = {"Content-Type": "application/json"}
    token = _agent_api_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = {
        "session_id": session_id,
        "post_url": post_url,
        "user_intent": user_intent,
        "selection_reason": selection_reason,
        "suggested_questions": suggested_questions or [],
    }
    try:
        resp = httpx.post(
            f"{base}/v1/internal/handoff_dispatch",
            json=body,
            headers=headers,
            timeout=HANDOFF_TIMEOUT_SECONDS,
        )
    except httpx.RequestError as exc:
        return json.dumps(
            {"ok": False, "error": f"agent_backend_unreachable: {exc}"},
            ensure_ascii=False,
        )
    try:
        payload = resp.json()
    except json.JSONDecodeError:
        payload = {"ok": False, "error": f"non_json_response status={resp.status_code}"}
    if resp.status_code >= 400 and "ok" not in payload:
        payload = {"ok": False, "error": f"agent_backend_status_{resp.status_code}", "body": payload}
    return json.dumps(payload, ensure_ascii=False)


def _normalize_questions(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for item in value[:6]:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


registry.register(
    name="request_human_handoff",
    toolset="springbrand_supost",
    schema={
        "name": "request_human_handoff",
        "description": (
            "Trigger a human operator to contact the SUpost seller of ONE specific post "
            "the user has chosen. Use AFTER you've narrowed to one post via supost_search "
            "/ supost_get_post / supost_check_alive AND the user has explicitly confirmed. "
            "This puts the run into awaiting_handoff — your final reply on this turn "
            "should be a brief acknowledgement (e.g. '已为你发起请求...'); do NOT promise "
            "specific timing or outcomes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "post_url": {
                    "type": "string",
                    "description": "Full URL of the chosen SUpost post (https://supost.com/post/index/...).",
                },
                "user_intent": {
                    "type": "string",
                    "description": (
                        "1–2 sentences capturing what the user actually wants from the "
                        "seller — target price, timing, special asks. Synthesize from the "
                        "full conversation, not just the latest message."
                    ),
                },
                "selection_reason": {
                    "type": "string",
                    "description": (
                        "1–2 sentences explaining why you chose this post over the other "
                        "candidates. Reference the user's stated preferences."
                    ),
                },
                "suggested_questions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "2–4 follow-up questions the operator should confirm with the seller.",
                },
            },
            "required": ["post_url", "user_intent"],
        },
    },
    handler=lambda args, **kw: springbrand_handoff(
        post_url=str(args.get("post_url") or ""),
        user_intent=str(args.get("user_intent") or ""),
        selection_reason=str(args.get("selection_reason") or ""),
        suggested_questions=_normalize_questions(args.get("suggested_questions")),
        session_id=str(kw.get("task_id") or ""),
    ),
    check_fn=check_springbrand_handoff_requirements,
)
