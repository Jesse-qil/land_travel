"""Agent 服务入口"""
import os

# Bypass system proxy for local/internal calls (httpx on Windows)
os.environ.setdefault("NO_PROXY", "127.0.0.1,localhost,::1")

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import agent
from core.context_cache import context_cache
from core.tool_registry import tool_registry
import tools  # noqa: F401 — calls register_all_tools()


def _log(msg: str):
    """Safe print that won't crash on emoji/unicode in Windows GBK console."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode())


async def _check_deepseek():
    """Startup: test DeepSeek API key with a minimal ping."""
    if not settings.DEEPSEEK_API_KEY:
        _log("[WARN] DeepSeek API Key not configured - AI disabled")
        return
    try:
        from core.llm_client import LLMClient, LLMMessage
        c = LLMClient()
        await c.chat(
            messages=[LLMMessage(role="user", content="ping")],
            max_tokens=5,
            timeout=10,
        )
        _log(f"[OK] DeepSeek API reachable ({settings.DEEPSEEK_MODEL})")
    except Exception as e:
        _log(f"[WARN] DeepSeek API check failed: {e}")
        _log("[WARN] AI features may not work - check key validity & balance")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        _log(f"[Startup] Travel Agent on port {settings.PORT}")
        tools_registered = list(tool_registry._tools.keys())
        _log(f"[Startup] Tools registered: {tools_registered if tools_registered else 'NONE'}")
        await _check_deepseek()
    except Exception as e:
        _log(f"[Startup] Warning: startup check failed: {e}")
    yield
    _log("[Shutdown] Agent cleaning up...")


app = FastAPI(
    title="Travel Agent",
    version="3.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent.router, prefix="/agent", tags=["Agent"])

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "travel-agent"}


@app.on_event("startup")
async def _start_cleanup_task():
    # 上下文过期清理（简化版，生产环境用 APScheduler）
    pass
