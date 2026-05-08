#!/usr/bin/env python3
"""SpringBrand shared catalog tool.

Reads the SpringBrand demo's local SQLite catalog so Hermes can ground
shopping recommendations in the same backend data the frontend renders.
"""

from __future__ import annotations

import functools
import json
import os
import sys
from pathlib import Path

from tools.registry import registry


DEFAULT_DEMO_ROOT = Path("/Users/qiuyanxin/Documents/code/springbrand/springbrand-fang-demo")


def _resolve_demo_root() -> Path:
    return Path(os.environ.get("SPRINGBRAND_DEMO_ROOT", DEFAULT_DEMO_ROOT)).expanduser()


@functools.lru_cache(maxsize=1)
def _load_catalog_backend():
    demo_root = _resolve_demo_root()
    if not demo_root.exists():
        raise FileNotFoundError(
            f"SpringBrand demo repo not found at {demo_root}. "
            "Set SPRINGBRAND_DEMO_ROOT if it lives elsewhere."
        )

    demo_root_str = str(demo_root)
    if demo_root_str not in sys.path:
        sys.path.insert(0, demo_root_str)

    import catalog_backend

    catalog_backend.ensure_catalog_db()
    return catalog_backend, demo_root


def check_springbrand_catalog_requirements() -> bool:
    try:
        _load_catalog_backend()
    except Exception:
        return False
    return True


def springbrand_catalog(
    action: str,
    query: str = "",
    surface: str = "",
    domain: str = "",
    store_id: str = "",
    limit: int = 6,
) -> str:
    catalog_backend, _demo_root = _load_catalog_backend()
    act = (action or "").strip().lower()

    if act == "search_products":
        results = catalog_backend.search_products(
            query=query,
            surface=(surface or "").strip(),
            domain=(domain or "").strip(),
            limit=max(1, min(int(limit or 6), 12)),
        )
        return json.dumps(
            {
                "action": act,
                "query": query,
                "surface": surface,
                "domain": domain,
                "results": results,
            },
            ensure_ascii=False,
        )

    if act == "get_store":
        if not store_id:
            return json.dumps({"error": "store_id is required for get_store"}, ensure_ascii=False)
        store = catalog_backend.get_store(store_id)
        if not store:
            return json.dumps({"error": f"unknown store_id: {store_id}"}, ensure_ascii=False)
        return json.dumps({"action": act, "store": store}, ensure_ascii=False)

    if act == "list_openstore_merchants":
        return json.dumps(
            {
                "action": act,
                "merchants": catalog_backend.list_openstore_merchants(),
            },
            ensure_ascii=False,
        )

    if act == "simulate_openstore_roundtrip":
        if not query:
            return json.dumps({"error": "query is required for simulate_openstore_roundtrip"}, ensure_ascii=False)
        return json.dumps(catalog_backend.simulate_openstore_roundtrip(query), ensure_ascii=False)

    return json.dumps(
        {
            "error": "unknown action",
            "action": action,
            "allowed": [
                "search_products",
                "get_store",
                "list_openstore_merchants",
                "simulate_openstore_roundtrip",
            ],
        },
        ensure_ascii=False,
    )


registry.register(
    name="springbrand_catalog",
    toolset="springbrand_catalog",
    schema={
        "name": "springbrand_catalog",
        "description": (
            "Query the shared SpringBrand demo catalog database. Use this for shopping lookups so "
            "recommendations stay grounded in the same products the frontend demo renders."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": (
                        "search_products | get_store | list_openstore_merchants | simulate_openstore_roundtrip"
                    ),
                },
                "query": {
                    "type": "string",
                    "description": "Buyer request or natural-language query for catalog search",
                },
                "surface": {
                    "type": "string",
                    "description": "Optional surface filter: shop | agent | openstore | selling",
                },
                "domain": {
                    "type": "string",
                    "description": "Optional domain filter: ecom | resale | local | openstore",
                },
                "store_id": {
                    "type": "string",
                    "description": "Store id for get_store",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max number of products to return for search_products",
                },
            },
            "required": ["action"],
        },
    },
    handler=lambda args, **kw: springbrand_catalog(
        action=str(args.get("action") or ""),
        query=str(args.get("query") or ""),
        surface=str(args.get("surface") or ""),
        domain=str(args.get("domain") or ""),
        store_id=str(args.get("store_id") or ""),
        limit=int(args.get("limit") or 6),
    ),
    check_fn=check_springbrand_catalog_requirements,
)
