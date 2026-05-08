"""Tests for OpenStore static catalog + demo tool."""

import json

import pytest

from tools.openstore_demo_catalog import (
    MERCHANTS,
    get_merchant,
    list_merchants,
    list_products,
    simulate_sp_a2a_roundtrip,
)
from tools.openstore_demo_tool import openstore_a2a_demo


def test_merchants_seeded():
    assert "meowant" in MERCHANTS
    assert "petkit" in MERCHANTS
    assert len(list_merchants()) == 3


def test_get_merchant_meowant():
    m = get_merchant("meowant")
    assert m is not None
    assert m["display_name"] == "Meowant"
    assert len(m["products"]) >= 2
    assert all(product.get("image_url", "").startswith("https://") for product in m["products"])
    assert all(product.get("specifications") for product in m["products"])
    assert all(product.get("source", {}).get("verified_on") == "2026-04-23" for product in m["products"])


def test_simulate_roundtrip_structure():
    out = simulate_sp_a2a_roundtrip("想买个自动喂食器，经常出差")
    assert out["demo"] is True
    assert "simulated_fanout_to_merchant_agents" in out
    assert len(out["simulated_fanout_to_merchant_agents"]) == 3
    assert out["recommendation"]["primary_merchant"] in {"petkit", "homerun"}
    assert out["recommendation"]["primary_merchant"] != "meowant"
    assert "meowant_spotlight_products" in out["recommendation"]


def test_simulate_roundtrip_litter_box_prefers_meowant_catalog():
    out = simulate_sp_a2a_roundtrip("我想买个猫砂盆，有什么推荐？")
    assert out["intent_scores"]["meowant"] > out["intent_scores"]["petkit"]
    assert any("猫砂盆" in p["name"] or "Litter Box" in p["name"] for p in out["recommendation"]["recommended_products"])
    meowant_reply = out["simulated_fanout_to_merchant_agents"][0]["merchant_agent_reply"]
    assert any("猫砂盆" in p["name"] or "Litter Box" in p["name"] for p in meowant_reply["candidate_products"])
    assert out["recommendation"]["meowant_feature_matches"]
    assert out["recommendation"]["meowant_feature_matches"][0]["product_sku"] == "MW-LITTER-ULTRA"
    assert out["recommendation"]["recommended_products"][0]["product_url"].startswith("https://")
    assert "演示" not in out["recommendation"]["recommended_products"][0]["name"]


def test_simulate_roundtrip_water_feature_match_prefers_meowant_fountain():
    out = simulate_sp_a2a_roundtrip("想要一款静音、好清洗的饮水机")
    assert out["recommendation"]["recommended_products"][0]["sku"] == "MW-FOUNTAIN-UV"
    assert any(
        match["product_sku"] == "MW-FOUNTAIN-UV"
        for match in out["recommendation"]["meowant_feature_matches"]
    )
    assert out["recommendation"]["recommended_products"][0]["image_url"].startswith("https://")


def test_pick_products_does_not_mix_unrelated_categories_for_litter_queries():
    out = simulate_sp_a2a_roundtrip("性价比猫砂盆，除味，空间大，声音小")
    recommended = out["recommendation"]["recommended_products"]

    assert recommended
    assert all("猫砂盆" in p["name"] or "Litter Box" in p["name"] for p in recommended)


@pytest.mark.parametrize(
    "action,extra,check",
    [
        ("list_merchants", {}, lambda d: len(d["merchants"]) == 3),
        (
            "get_merchant",
            {"merchant_slug": "petkit"},
            lambda d: d["merchant"]["slug"] == "petkit",
        ),
        (
            "list_products",
            {"merchant_slug": "meowant"},
            lambda d: len(d["products"]) >= 2,
        ),
    ],
)
def test_openstore_a2a_demo_actions(action, extra, check):
    raw = openstore_a2a_demo(
        action=action,
        merchant_slug=extra.get("merchant_slug", ""),
        user_message=extra.get("user_message", ""),
    )
    data = json.loads(raw)
    assert check(data)


def test_openstore_a2a_demo_simulate_requires_message():
    raw = openstore_a2a_demo(action="simulate_sp_intent_flow", user_message="")
    data = json.loads(raw)
    assert "error" in data


def test_openstore_a2a_demo_simulate():
    raw = openstore_a2a_demo(
        action="simulate_sp_intent_flow",
        user_message="对比一下饮水机和保修",
    )
    data = json.loads(raw)
    assert data["demo"] is True
    assert "cross_merchant_comparison" in data
