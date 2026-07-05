"""AI 路由：行程生成 / 多轮问答

通过 HTTP 调用独立部署的 Agent 服务（travel-agent，端口 8001）。
Agent 服务无 DeepSeek Key 或风控命中时返回 N/A，主项目透传降级。
"""
import httpx
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from typing import Literal

from schemas.common import ok, fail, ErrorCodes
from config import settings

router = APIRouter()


class PlanRequest(BaseModel):
    city: str
    days: int = Field(default=3, ge=1, le=7)
    style: list[str] = []
    budget: Literal["low", "medium", "high"] = "medium"
    companions: str = "独自"


class AskRequest(BaseModel):
    session_id: str | None = None
    question: str = Field(min_length=1, max_length=500)


async def _call_agent(path: str, payload: dict, request: Request) -> dict | None:
    """调用 Agent 服务，失败返回 None"""
    user_id = request.state.user_id
    guest_id = request.state.guest_id
    payload = {**payload, "user_id": user_id, "guest_id": guest_id}
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{settings.AGENT_BASE_URL}{path}",
                json=payload,
                headers={"X-Service-Token": settings.BACKEND_SERVICE_TOKEN},
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.TimeoutException:
        return {"code": ErrorCodes.AI_UNAVAILABLE, "message": "AI 服务响应超时", "data": None}
    except httpx.ConnectError:
        return {"code": ErrorCodes.AI_UNAVAILABLE, "message": "AI 服务暂不可用", "data": None}
    except Exception as e:
        return {"code": ErrorCodes.AI_UNAVAILABLE, "message": f"AI 服务异常: {e}", "data": None}


@router.post("/plan")
async def generate_plan(request: Request, body: PlanRequest):
    """AI 智能行程生成"""
    result = await _call_agent("/agent/plan", body.model_dump(), request)
    if result is None:
        return fail(ErrorCodes.AI_UNAVAILABLE, "AI 服务暂不可用（N/A）")
    return result


@router.post("/ask")
async def ask_question(request: Request, body: AskRequest):
    """AI 多轮问答"""
    result = await _call_agent("/agent/ask", body.model_dump(), request)
    if result is None:
        return fail(ErrorCodes.AI_UNAVAILABLE, "AI 服务暂不可用（N/A）")
    return result
