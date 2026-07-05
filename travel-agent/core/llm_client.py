"""LLM 客户端 — DeepSeek API 异步封装"""
import asyncio
import httpx
from typing import Literal
from pydantic import BaseModel

from config import settings


class LLMMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_call_id: str | None = None
    tool_calls: list[dict] | None = None


class ToolCallRequest(BaseModel):
    id: str
    name: str
    arguments: dict


class LLMResponse(BaseModel):
    content: str | None = None
    tool_calls: list[ToolCallRequest] | None = None
    tokens_in: int = 0
    tokens_out: int = 0
    finish_reason: str = "stop"


class LLMClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.base_url = base_url or settings.DEEPSEEK_BASE_URL
        self.model = model or settings.DEEPSEEK_MODEL

    async def chat(
        self,
        messages: list[LLMMessage],
        tools: list[dict] | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        timeout: float | None = None,
    ) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": [m.model_dump(exclude_none=True) for m in messages],
            "max_tokens": max_tokens or settings.LLM_MAX_TOKENS,
            "temperature": temperature if temperature is not None else settings.LLM_TEMPERATURE,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=timeout or settings.LLM_TIMEOUT, proxy=None, trust_env=False) as client:
                resp = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()

            choice = data["choices"][0]
            msg = choice["message"]
            tool_calls = None
            if msg.get("tool_calls"):
                import json
                tool_calls = [
                    ToolCallRequest(
                        id=tc["id"],
                        name=tc["function"]["name"],
                        arguments=json.loads(tc["function"]["arguments"]),
                    )
                    for tc in msg["tool_calls"]
                ]

            return LLMResponse(
                content=msg.get("content"),
                tool_calls=tool_calls,
                tokens_in=data.get("usage", {}).get("prompt_tokens", 0),
                tokens_out=data.get("usage", {}).get("completion_tokens", 0),
                finish_reason=choice.get("finish_reason", "stop"),
            )
        except httpx.TimeoutException:
            raise asyncio.TimeoutError("LLM 请求超时")
        except Exception as e:
            raise RuntimeError(f"LLM 调用失败: {e}")


llm_client = LLMClient()
