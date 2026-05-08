"""Tests for SpringBrand/OpenStore gateway commands."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from gateway.config import GatewayConfig, Platform, PlatformConfig
from gateway.platforms.base import MessageEvent
from gateway.session import SessionEntry, SessionSource, build_session_key


def _make_source() -> SessionSource:
    return SessionSource(
        platform=Platform.TELEGRAM,
        user_id="buyer-1",
        chat_id="chat-1",
        user_name="tester",
        chat_type="dm",
    )


def _make_event(text: str) -> MessageEvent:
    return MessageEvent(text=text, source=_make_source(), message_id="m1")


def _make_runner():
    from gateway.run import GatewayRunner

    runner = object.__new__(GatewayRunner)
    runner.config = GatewayConfig(
        platforms={Platform.TELEGRAM: PlatformConfig(enabled=True, token="***")}
    )
    runner.adapters = {Platform.TELEGRAM: MagicMock(send=AsyncMock())}
    runner.hooks = SimpleNamespace(emit=AsyncMock(), loaded_hooks=False)
    runner.session_store = MagicMock()
    runner.session_store.get_or_create_session.return_value = SessionEntry(
        session_key=build_session_key(_make_source()),
        session_id="sess-1",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        platform=Platform.TELEGRAM,
        chat_type="dm",
    )
    runner.session_store.load_transcript.return_value = []
    runner.session_store.has_any_sessions.return_value = True
    runner._running_agents = {}
    runner._running_agents_ts = {}
    runner._pending_messages = {}
    runner._pending_approvals = {}
    runner._session_db = None
    runner._reasoning_config = None
    runner._provider_routing = {}
    runner._fallback_model = None
    runner._show_reasoning = False
    runner._voice_mode = {}
    runner._draining = False
    runner._busy_ack_ts = {}
    runner._is_user_authorized = lambda _source: True
    runner._set_session_env = lambda _context: None
    runner._should_send_voice_reply = lambda *_args, **_kwargs: False
    runner._send_voice_reply = AsyncMock()
    runner._capture_gateway_honcho_if_configured = lambda *args, **kwargs: None
    runner._emit_gateway_run_progress = AsyncMock()
    runner._handle_message_with_agent = AsyncMock(return_value="agent handled")
    return runner


@pytest.mark.asyncio
async def test_start_command_returns_springbrand_welcome():
    runner = _make_runner()

    result = await runner._handle_start_command(_make_event("/start"))

    assert "SpringBrand" in result
    assert "/sp-buy" in result
    assert "/sell" in result
    assert "direct product recommendations with links" in result


@pytest.mark.asyncio
async def test_buy_command_without_payload_returns_usage():
    runner = _make_runner()

    result = await runner._handle_buy_command(_make_event("/buy"))

    assert result is not None
    assert "Usage" in result
    assert "/buy <what you need>" in result


@pytest.mark.asyncio
async def test_buy_command_rewrites_into_agent_turn():
    runner = _make_runner()
    event = _make_event("/buy I need a quiet cat water fountain")

    result = await runner._handle_message(event)

    assert result == "agent handled"
    forwarded_event = runner._handle_message_with_agent.await_args.args[0]
    assert "shopping intent" in forwarded_event.text
    assert "Buyer request: I need a quiet cat water fountain" in forwarded_event.text


@pytest.mark.asyncio
async def test_sp_buy_without_payload_returns_usage():
    runner = _make_runner()

    result = await runner._handle_sp_buy_command(_make_event("/sp-buy"))

    assert "Usage" in result
    assert "/sp-buy <what you need>" in result


@pytest.mark.asyncio
async def test_sp_buy_uses_demo_path_and_bypasses_agent():
    runner = _make_runner()
    event = _make_event("/sp-buy 我想买个猫砂盆，优先 Meowant")

    result = await runner._handle_message(event)

    assert "首推" in result
    assert "Meowant" in result
    assert "猫砂盆" in result
    assert "商品链接：" in result
    assert "https://meowant.com/products/meowant-self-cleaning-cat-litter-box-mw-sc02-white" in result
    assert "Meowant 商品卡（官网快照）" in result
    assert "快照日期：2026-04-23" in result
    assert "![自清洁猫砂盆 MW-SC02（白色）" in result
    assert "cdn.shopify.com" in result
    assert "Demo" not in result
    assert "演示" not in result
    runner._handle_message_with_agent.assert_not_awaited()


@pytest.mark.asyncio
async def test_sp_buy_alias_sp_buy_with_underscore_works():
    runner = _make_runner()
    event = _make_event("/sp_buy want a quiet water fountain")

    result = await runner._handle_message(event)

    assert "商品链接：" in result
    assert "Meowant" in result
    assert "Meowant 商品卡（官网快照）" in result
    assert "![无线宠物饮水机" in result
    runner._handle_message_with_agent.assert_not_awaited()


@pytest.mark.asyncio
async def test_sp_buy_runs_even_when_another_agent_is_active():
    runner = _make_runner()
    session_key = build_session_key(_make_source())
    runner._running_agents[session_key] = MagicMock()

    result = await runner._handle_message(_make_event("/sp-buy 我想买猫砂盆"))

    assert "首推" in result
    assert "Meowant" in result
    runner._handle_message_with_agent.assert_not_awaited()


@pytest.mark.asyncio
async def test_sell_command_rewrites_into_agent_turn():
    runner = _make_runner()
    event = _make_event("/sell I run a pet supplies brand and want a Telegram store")

    result = await runner._handle_message(event)

    assert result == "agent handled"
    forwarded_event = runner._handle_message_with_agent.await_args.args[0]
    assert "seller onboarding request" in forwarded_event.text
    assert "Seller request: I run a pet supplies brand and want a Telegram store" in forwarded_event.text
