"""FastAPI 主应用入口（异步）"""
import os

# Bypass system proxy for local/internal calls (httpx on Windows)
os.environ.setdefault("NO_PROXY", "127.0.0.1,localhost,::1")

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from config import settings
from routers import cities, weather, user, ai, admin, feedback, auth
from middleware.auth import AuthMiddleware
from middleware.rate_limit import RateLimitMiddleware
from schemas.common import ok

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[Startup] {settings.APP_NAME} running on port {settings.PORT}")
    yield
    print("[Shutdown] cleaning up...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(cities.router, prefix="/api", tags=["城市/路书"])
app.include_router(weather.router, prefix="/api", tags=["天气"])
app.include_router(user.router, prefix="/api", tags=["用户/UGC"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(admin.router, prefix="/api/admin", tags=["后台管理"])
app.include_router(feedback.router, prefix="/api", tags=["反馈"])


@app.get("/api/info")
async def service_info():
    """Diagnostic endpoint — shows all service statuses."""
    import httpx
    agent_ok = False
    agent_msg = ""
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{settings.AGENT_BASE_URL}/health")
            agent_ok = r.status_code == 200
            agent_msg = "reachable" if agent_ok else f"HTTP {r.status_code}"
    except Exception as e:
        agent_msg = str(e)

    return ok({
        "backend": {"version": settings.VERSION, "debug": settings.DEBUG},
        "agent": {
            "url": settings.AGENT_BASE_URL,
            "reachable": agent_ok,
            "detail": agent_msg,
        },
        "deepseek": {
            "configured": bool(settings.DEEPSEEK_API_KEY),
            "key_preview": settings.DEEPSEEK_API_KEY[:12] + "..." if settings.DEEPSEEK_API_KEY else "",
        },
        "supabase": {
            "configured": bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY),
        },
        "weather": {
            "configured": bool(settings.QWEATHER_API_KEY),
        },
    })


@app.get("/health")
async def health():
    return {"code": 0, "message": "ok", "data": {"status": "healthy"}}


# SPA 静态资源 serve（生产部署由 Nginx 承担，开发联调由后端兜底）
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str, request: Request):
        file_path = FRONTEND_DIST / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        # Never cache index.html so browser always gets latest chunks
        return FileResponse(
            FRONTEND_DIST / "index.html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
