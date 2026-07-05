"""Agent 路由 — 行程生成 / 多轮问答"""
import asyncio
import json
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from fastapi import APIRouter, Request

from schemas.common import ok, fail, ErrorCodes
from schemas.agent import PlanRequest, AskRequest
from core import llm_client, tool_registry, output_validator, context_cache, cost_guard
from core.llm_client import LLMMessage
from config import settings

router = APIRouter()

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _utc_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


@router.post("/plan")
async def generate_plan(request: Request, body: PlanRequest):
    """AI 智能行程生成（轻量 ToolCall + 双层校验 + 降级）"""
    user_id = body.user_id
    client_ip = _client_ip(request)

    # Step 0: 检查 DeepSeek API Key 是否配置
    if not settings.DEEPSEEK_API_KEY:
        return fail(
            ErrorCodes.AI_UNAVAILABLE,
            "AI 行程生成暂不可用（N/A）：DeepSeek API Key 未配置",
        )

    # Step 1: 预扣风控
    guard_result = await cost_guard.check(user_id, client_ip)
    if not guard_result.allowed:
        return fail(ErrorCodes.AI_UNAVAILABLE, guard_result.reason)

    # Step 2: 组装 Prompt
    system_prompt = _load_prompt("plan_generation.txt")
    user_msg = (
        f"请为以下需求生成行程：\n"
        f"- 城市：{body.city}\n"
        f"- 天数：{body.days} 天\n"
        f"- 风格偏好：{', '.join(body.style) if body.style else '不限'}\n"
        f"- 预算：{body.budget}\n"
        f"- 同行人：{body.companions}\n\n"
        f"返回 JSON 格式：{{\"items\": [{{\"day\": 1, \"weather_note\": \"\", \"spots\": [{{\"name\": \"\", \"time\": \"\", \"activity\": \"\", \"poi_status\": \"\", \"tip\": \"\", \"lat\": 0, \"lng\": 0}}]}}], \"budget_estimate\": 0}}"
    )

    messages = [
        LLMMessage(role="system", content=system_prompt),
        LLMMessage(role="user", content=user_msg),
    ]

    tools = tool_registry.get_all_definitions()
    tool_registry.reset_call_counts()

    # Step 3: ToolCall 循环（最多 MAX_TOOL_ROUNDS 轮）
    try:
        for round_idx in range(settings.MAX_TOOL_ROUNDS):
            response = await llm_client.chat(messages=messages, tools=tools)

            if not response.tool_calls:
                break

            assistant_msg = LLMMessage(
                role="assistant",
                content=response.content or "",
                tool_calls=[
                    {"id": tc.id, "type": "function", "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)}}
                    for tc in response.tool_calls
                ],
            )
            messages.append(assistant_msg)

            for tc in response.tool_calls:
                result = await tool_registry.dispatch(tc.name, tc.arguments)
                messages.append(
                    LLMMessage(role="tool", content=result, tool_call_id=tc.id)
                )

        # 最终获取内容
        if response.content is None and response.tool_calls:
            response = await llm_client.chat(messages=messages, tools=None)

    except asyncio.TimeoutError:
        return fail(ErrorCodes.AI_UNAVAILABLE, "AI 生成超时，请稍后重试")
    except Exception as e:
        return fail(ErrorCodes.AI_UNAVAILABLE, f"AI 生成失败: {e}")

    # Step 4: 双层校验
    validation = output_validator.validate(response.content or "")
    if not validation.is_valid:
        return fail(
            ErrorCodes.AI_UNAVAILABLE,
            "AI 输出格式异常，请重试",
            {"errors": validation.errors, "warnings": validation.warnings},
        )

    # Step 5: 记录用量
    cost = (response.tokens_in * 0.001 + response.tokens_out * 0.002) / 1000  # 估算
    cost_guard.record_usage(user_id, client_ip, response.tokens_in, response.tokens_out, cost)

    # Step 6: 返回
    return ok({
        "plan": validation.data,
        "from_cache": False,
        "generated_at": _utc_iso(datetime.now()),
        "warnings": validation.warnings,
    })


@router.post("/ask")
async def ask_question(request: Request, body: AskRequest):
    """AI 多轮问答（短时上下文缓存，不启用 ToolCall 节省成本）"""
    user_id = body.user_id
    client_ip = _client_ip(request)

    # 检查 DeepSeek API Key 是否配置
    if not settings.DEEPSEEK_API_KEY:
        return fail(
            ErrorCodes.AI_UNAVAILABLE,
            "AI 问答暂不可用（N/A）：DeepSeek API Key 未配置",
        )

    guard_result = await cost_guard.check(user_id, client_ip)
    if not guard_result.allowed:
        return fail(ErrorCodes.AI_UNAVAILABLE, guard_result.reason)

    session_id, history = context_cache.get_or_create(body.session_id)
    system_prompt = _load_prompt("travel_qa.txt")

    messages = [LLMMessage(role="system", content=system_prompt)]
    for msg in history:
        messages.append(LLMMessage(role=msg["role"], content=msg["content"]))
    messages.append(LLMMessage(role="user", content=body.question))

    try:
        response = await llm_client.chat(messages=messages, tools=None)
    except asyncio.TimeoutError:
        return fail(ErrorCodes.AI_UNAVAILABLE, "AI 回复超时")
    except Exception as e:
        return fail(ErrorCodes.AI_UNAVAILABLE, f"AI 回复失败: {e}")

    answer = response.content or ""
    context_cache.append(session_id, "user", body.question)
    context_cache.append(session_id, "assistant", answer)

    cost = (response.tokens_in * 0.001 + response.tokens_out * 0.002) / 1000
    cost_guard.record_usage(user_id, client_ip, response.tokens_in, response.tokens_out, cost)

    expire_at = datetime.now(timezone.utc) + timedelta(seconds=settings.CONTEXT_TTL)

    return ok({
        "session_id": session_id,
        "answer": answer,
        "context_expire_at": _utc_iso(expire_at),
    })


@router.get("/cost/today")
async def daily_cost():
    """查询今日累计费用"""
    return ok({"daily_cost": cost_guard.daily_cost(), "budget": settings.AI_DAILY_BUDGET})
