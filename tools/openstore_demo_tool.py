#!/usr/bin/env python3
"""
OpenStore demo tool — simulates SP ↔ merchant A2A using in-process catalog.

Enable toolset ``openstore_demo`` (or preset ``hermes-openstore-sp``) on the
Telegram profile that runs your OpenStore bot.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from tools.openstore_demo_catalog import (
    get_merchant,
    list_merchants,
    list_products,
    simulate_sp_a2a_roundtrip,
)
from tools.registry import registry


def check_openstore_demo_requirements() -> bool:
    return True


def openstore_a2a_demo(
    action: str,
    merchant_slug: str = "",
    user_message: str = "",
    task_id: Optional[str] = None,
) -> str:
    act = (action or "").strip().lower()
    slug = (merchant_slug or "").strip().lower()

    if act == "list_merchants":
        return json.dumps({"merchants": list_merchants()}, ensure_ascii=False)

    if act == "get_merchant":
        if not slug:
            return json.dumps({"error": "merchant_slug is required for get_merchant"})
        m = get_merchant(slug)
        if not m:
            return json.dumps({"error": f"unknown merchant: {slug}"}, ensure_ascii=False)
        return json.dumps({"merchant": m}, ensure_ascii=False)

    if act == "list_products":
        if not slug:
            return json.dumps({"error": "merchant_slug is required for list_products"})
        products = list_products(slug)
        if products is None:
            return json.dumps({"error": f"unknown merchant: {slug}"}, ensure_ascii=False)
        return json.dumps({"merchant_slug": slug, "products": products}, ensure_ascii=False)

    if act in ("simulate_sp_intent_flow", "simulate", "roundtrip"):
        msg = (user_message or "").strip()
        if not msg:
            return json.dumps(
                {"error": "user_message is required for simulate_sp_intent_flow"},
                ensure_ascii=False,
            )
        return json.dumps(simulate_sp_a2a_roundtrip(msg), ensure_ascii=False)

    return json.dumps(
        {
            "error": "unknown action",
            "action": action,
            "allowed": [
                "list_merchants",
                "get_merchant",
                "list_products",
                "simulate_sp_intent_flow",
            ],
        },
        ensure_ascii=False,
    )


registry.register(
    name="openstore_a2a_demo",
    toolset="openstore_demo",
    schema={
        "name": "openstore_a2a_demo",
        "description": (
            "OpenStore 演示：用内置静态库模拟 Springbrand OpenStore 上 **SP 意图撮合 agent** "
            "与多家 **商家 agent**（Meowant、PETKIT 小佩、霍曼等）之间的 A2A 往返。"
            "不会发起真实网络 A2A。典型用法：对用户一句自然语言购物意图调用 "
            "`simulate_sp_intent_flow` 拿到「伪 fan-out」与各店回复摘要，再据此生成推荐与竞品对比。"
            "也可用 `list_merchants` / `get_merchant` / `list_products` 拉取演示商品与政策字段。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": (
                        "list_merchants | get_merchant | list_products | simulate_sp_intent_flow"
                    ),
                },
                "merchant_slug": {
                    "type": "string",
                    "description": "商家 slug：meowant | petkit | homerun（get_merchant / list_products 必填）",
                },
                "user_message": {
                    "type": "string",
                    "description": "用户原始消息（simulate_sp_intent_flow 必填），可与 TG 侧原文一致",
                },
            },
            "required": ["action"],
        },
    },
    handler=lambda args, **kw: openstore_a2a_demo(
        action=str(args.get("action") or ""),
        merchant_slug=str(args.get("merchant_slug") or ""),
        user_message=str(args.get("user_message") or ""),
        task_id=kw.get("task_id"),
    ),
    check_fn=check_openstore_demo_requirements,
)
