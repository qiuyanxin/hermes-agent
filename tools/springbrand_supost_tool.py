#!/usr/bin/env python3
"""SpringBrand SUpost concierge tool.

Adapter for the SUpost (Stanford community board) listing search,
backed by the supost-adapter HTTP service in the springbrand
a2a-commerce demo. Unlike springbrand_catalog_tool which loads a
sibling demo's SQLite via sys.path hack, this tool is HTTP-only
so it works the same locally and on Railway production.
"""
from __future__ import annotations

import json
import os

import httpx

from tools.registry import registry


SUPOST_ADAPTER_URL_DEFAULT = "http://127.0.0.1:8788"
SUPOST_TIMEOUT_SECONDS = 20.0


def _supost_base_url() -> str:
    return (os.environ.get("SUPOST_ADAPTER_URL") or SUPOST_ADAPTER_URL_DEFAULT).rstrip("/")


def _supost_token() -> str:
    return os.environ.get("SUPOST_ADAPTER_API_TOKEN", "")


def check_springbrand_supost_requirements() -> bool:
    # We don't probe /health on every registry refresh — startup would slow
    # to a crawl when the adapter is offline. Tool handler surfaces
    # connection errors as structured JSON, so the LLM can react.
    return bool(_supost_base_url())


def _post_tool(tool_name: str, input_payload: dict) -> dict:
    # supost-adapter expects an envelope: { context: {scopes, ...}, input: {...} }.
    # All three supost_* tools require scope `catalog:read`.
    url = f"{_supost_base_url()}/tools/{tool_name}"
    headers = {"Content-Type": "application/json"}
    token = _supost_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    envelope = {
        "context": {
            "scopes": ["catalog:read"],
            "actor_type": "agent",
            "actor_id": "hermes-agent",
        },
        "input": input_payload,
    }
    try:
        resp = httpx.post(url, json=envelope, headers=headers, timeout=SUPOST_TIMEOUT_SECONDS)
    except httpx.RequestError as exc:
        return {"error": "adapter_unreachable", "detail": str(exc)}
    if resp.status_code >= 400:
        return {
            "error": "adapter_http_error",
            "status": resp.status_code,
            "body": resp.text[:500],
        }
    try:
        return resp.json()
    except json.JSONDecodeError:
        return {"error": "adapter_returned_invalid_json", "body": resp.text[:500]}


def springbrand_supost(
    action: str,
    query: str = "",
    post_url: str = "",
    category: int | None = None,
    limit: int = 5,
) -> str:
    act = (action or "").strip().lower()

    if act == "supost_search":
        if not query:
            return json.dumps({"error": "query is required for supost_search"}, ensure_ascii=False)
        payload: dict = {"query": query, "limit": max(1, min(int(limit or 5), 20))}
        if category:
            payload["category"] = int(category)
        result = _post_tool("supost_search", payload)
        return json.dumps({"action": act, "query": query, "result": result}, ensure_ascii=False)

    if act == "supost_get_post":
        if not post_url:
            return json.dumps({"error": "post_url is required for supost_get_post"}, ensure_ascii=False)
        result = _post_tool("supost_get_post", {"post_url": post_url})
        return json.dumps({"action": act, "post_url": post_url, "result": result}, ensure_ascii=False)

    if act == "supost_check_alive":
        if not post_url:
            return json.dumps({"error": "post_url is required for supost_check_alive"}, ensure_ascii=False)
        result = _post_tool("supost_check_alive", {"post_url": post_url})
        return json.dumps({"action": act, "post_url": post_url, "result": result}, ensure_ascii=False)

    return json.dumps(
        {
            "error": "unknown action",
            "action": action,
            "allowed": ["supost_search", "supost_get_post", "supost_check_alive"],
        },
        ensure_ascii=False,
    )


registry.register(
    name="springbrand_supost",
    toolset="springbrand_supost",
    schema={
        "name": "springbrand_supost",
        "description": (
            "Search and inspect SUpost (Stanford community board) listings. SUpost is "
            "Stanford-only and English-only — translate non-English queries to English "
            "BEFORE calling supost_search (床垫→mattress, 桌子→desk, 椅子→chair, "
            "显示器→monitor, 自行车→bike/bicycle, 转租→sublet/sublease). Use for "
            "student secondhand goods, sublease/housing, services, and jobs. Always "
            "supost_get_post (or supost_check_alive at minimum) before recommending a "
            "specific post — it confirms the post is still alive."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "supost_search | supost_get_post | supost_check_alive",
                },
                "query": {
                    "type": "string",
                    "description": (
                        "ENGLISH search keywords for supost_search (e.g. 'mattress', "
                        "'sublease summer', 'used iphone'). Required for supost_search."
                    ),
                },
                "post_url": {
                    "type": "string",
                    "description": (
                        "Full SUpost URL like https://supost.com/post/index/130076211. "
                        "Required for supost_get_post / supost_check_alive."
                    ),
                },
                "category": {
                    "type": "integer",
                    "description": (
                        "Optional category 1=Buy/Sell, 2=Services, 3=Jobs, 4=Housing, "
                        "5=Furniture, 7=Events, 8=Personals, 9=Other. Omit for broad search."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results for supost_search (1-20, default 5).",
                },
            },
            "required": ["action"],
        },
    },
    handler=lambda args, **kw: springbrand_supost(
        action=str(args.get("action") or ""),
        query=str(args.get("query") or ""),
        post_url=str(args.get("post_url") or ""),
        category=args.get("category") if args.get("category") not in (None, "") else None,
        limit=int(args.get("limit") or 5),
    ),
    check_fn=check_springbrand_supost_requirements,
)
