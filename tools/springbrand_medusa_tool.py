#!/usr/bin/env python3
"""SpringBrand Medusa buyer tool.

Adapter for the Medusa marketplace catalog (search / discover merchants /
get product / check inventory) and the demo-side propose_bundle dispatcher.

Routing:
    search_products / discover_merchants / get_product / check_inventory
        → POST {COMMERCE_ADAPTER_URL}/tools/<tool_name>
    propose_bundle
        → POST {AGENT_BACKEND_INTERNAL_URL}/v1/internal/propose_bundle_dispatch
        (because the demo storefront subscribes to demo run_events for the
        bundle card render — propose_bundle is a side-effect tool whose
        canonical state lives in demo's PG, mirrors the request_human_handoff
        pattern in springbrand_handoff_tool.py)

Correlation: propose_bundle uses the demo session_id (Hermes passes
``session_id`` to the tool handler as ``task_id``) to recover the demo
run from a Redis hint written before /v1/runs is invoked.
"""
from __future__ import annotations

import json
import os
from typing import Any, List, Optional

import httpx

from tools.registry import registry


COMMERCE_ADAPTER_URL_DEFAULT = "http://127.0.0.1:8787"
COMMERCE_TIMEOUT_SECONDS = 25.0


def _commerce_base_url() -> str:
    return (os.environ.get("COMMERCE_ADAPTER_URL") or COMMERCE_ADAPTER_URL_DEFAULT).rstrip("/")


def _commerce_token() -> str:
    return os.environ.get("COMMERCE_ADAPTER_API_TOKEN", "")


def _agent_backend_url() -> str:
    return (os.environ.get("AGENT_BACKEND_INTERNAL_URL") or "").rstrip("/")


def _agent_api_token() -> str:
    return os.environ.get("AGENT_API_TOKEN", "")


def check_springbrand_medusa_requirements() -> bool:
    return bool(_commerce_base_url())


# ---------------------------------------------------------------------------
# commerce-adapter routes (read-only catalog + inventory)
# ---------------------------------------------------------------------------

def _post_adapter_tool(tool_name: str, scopes: List[str], input_payload: dict) -> dict:
    url = f"{_commerce_base_url()}/tools/{tool_name}"
    headers = {"Content-Type": "application/json"}
    token = _commerce_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    envelope = {
        "context": {
            "scopes": scopes,
            "actor_type": "agent",
            "actor_id": "hermes-agent",
        },
        "input": input_payload,
    }
    try:
        resp = httpx.post(url, json=envelope, headers=headers, timeout=COMMERCE_TIMEOUT_SECONDS)
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


# ---------------------------------------------------------------------------
# propose_bundle (side-effect — proxies to demo)
# ---------------------------------------------------------------------------

def _post_propose_bundle(session_id: str, label: str, items: List[dict], intro: str) -> dict:
    base = _agent_backend_url()
    if not base:
        return {"ok": False, "error": "AGENT_BACKEND_INTERNAL_URL not configured on hermes-agent"}
    if not session_id:
        return {"ok": False, "error": "missing session_id (Hermes runtime did not propagate task_id)"}

    headers = {"Content-Type": "application/json"}
    token = _agent_api_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    headers["X-Tenant-Id"] = os.environ.get("AGENT_DEFAULT_TENANT", "tenant_demo")

    body = {"session_id": session_id, "label": label, "items": items, "intro": intro}
    try:
        resp = httpx.post(
            f"{base}/v1/internal/propose_bundle_dispatch",
            json=body,
            headers=headers,
            timeout=COMMERCE_TIMEOUT_SECONDS,
        )
    except httpx.RequestError as exc:
        return {"ok": False, "error": f"agent_backend_unreachable: {exc}"}
    try:
        payload = resp.json()
    except json.JSONDecodeError:
        payload = {"ok": False, "error": f"non_json_response status={resp.status_code}"}
    if resp.status_code >= 400 and "ok" not in payload:
        payload = {"ok": False, "error": f"agent_backend_status_{resp.status_code}", "body": payload}
    return payload


# ---------------------------------------------------------------------------
# Action dispatch
# ---------------------------------------------------------------------------

def springbrand_medusa(
    action: str,
    query: str = "",
    product_id: str = "",
    vendor_handle: str = "",
    limit: int = 10,
    label: str = "",
    items: Optional[List[dict]] = None,
    intro: str = "",
    session_id: str = "",
) -> str:
    act = (action or "").strip().lower()

    if act == "search_products":
        if not query:
            return json.dumps({"error": "query is required for search_products"}, ensure_ascii=False)
        payload: dict = {"query": query, "limit": max(1, min(int(limit or 10), 50))}
        if vendor_handle:
            payload["vendor_handle"] = vendor_handle
        result = _post_adapter_tool("search_products", ["catalog:read"], payload)
        return json.dumps({"action": act, "query": query, "result": result}, ensure_ascii=False)

    if act == "discover_merchants":
        payload = {"query": query} if query else {}
        if vendor_handle:
            payload["vendor_handle"] = vendor_handle
        result = _post_adapter_tool("discover_merchants", ["catalog:read"], payload)
        return json.dumps({"action": act, "result": result}, ensure_ascii=False)

    if act == "get_product":
        if not product_id:
            return json.dumps({"error": "product_id is required for get_product"}, ensure_ascii=False)
        result = _post_adapter_tool("get_product", ["catalog:read"], {"product_id": product_id})
        return json.dumps({"action": act, "product_id": product_id, "result": result}, ensure_ascii=False)

    if act == "check_inventory":
        if not product_id:
            return json.dumps({"error": "product_id is required for check_inventory"}, ensure_ascii=False)
        result = _post_adapter_tool("check_inventory", ["inventory:read"], {"product_id": product_id})
        return json.dumps({"action": act, "product_id": product_id, "result": result}, ensure_ascii=False)

    if act == "propose_bundle":
        cleaned = items if isinstance(items, list) else []
        if not cleaned:
            return json.dumps({"error": "items is required for propose_bundle (non-empty list)"}, ensure_ascii=False)
        result = _post_propose_bundle(
            session_id=session_id,
            label=label or "Recommended bundle",
            items=cleaned,
            intro=intro or "",
        )
        return json.dumps({"action": act, "result": result}, ensure_ascii=False)

    return json.dumps(
        {
            "error": "unknown action",
            "action": action,
            "allowed": [
                "search_products",
                "discover_merchants",
                "get_product",
                "check_inventory",
                "propose_bundle",
            ],
        },
        ensure_ascii=False,
    )


registry.register(
    name="springbrand_medusa",
    toolset="springbrand_medusa",
    schema={
        "name": "springbrand_medusa",
        "description": (
            "Search and recommend products from the SpringBrand Medusa marketplace catalog. "
            "Supports catalog search, vendor discovery, product detail / inventory lookups, "
            "and the final propose_bundle commit (REQUIRED — the storefront only renders a "
            "bundle card when propose_bundle fires). Use action='search_products' first, then "
            "action='get_product' for details if needed, then action='propose_bundle' to "
            "commit. NEVER skip propose_bundle except when catalog truly returns zero matches."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "search_products | discover_merchants | get_product | check_inventory | propose_bundle",
                },
                "query": {
                    "type": "string",
                    "description": "Natural-language search query for search_products / discover_merchants.",
                },
                "product_id": {
                    "type": "string",
                    "description": "Medusa product id (e.g. prod_xxxx). Required for get_product / check_inventory.",
                },
                "vendor_handle": {
                    "type": "string",
                    "description": "Optional vendor handle filter for search_products / discover_merchants.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results for search_products (1-50, default 10).",
                },
                "label": {
                    "type": "string",
                    "description": "Bundle label shown on the card (e.g. 'Birthday gift'). Required for propose_bundle.",
                },
                "items": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": (
                        "Bundle items for propose_bundle. Each item: "
                        "{id: string, title: string, price: number, currency?: string, "
                        "vendor?: string, image_url?: string, url?: string}."
                    ),
                },
                "intro": {
                    "type": "string",
                    "description": "Optional 1-2 sentence intro for the bundle card.",
                },
            },
            "required": ["action"],
        },
    },
    handler=lambda args, **kw: springbrand_medusa(
        action=str(args.get("action") or ""),
        query=str(args.get("query") or ""),
        product_id=str(args.get("product_id") or ""),
        vendor_handle=str(args.get("vendor_handle") or ""),
        limit=int(args.get("limit") or 10),
        label=str(args.get("label") or ""),
        items=args.get("items") if isinstance(args.get("items"), list) else None,
        intro=str(args.get("intro") or ""),
        session_id=str(kw.get("task_id") or ""),
    ),
    check_fn=check_springbrand_medusa_requirements,
)
