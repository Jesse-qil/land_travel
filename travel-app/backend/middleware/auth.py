"""认证中间件：JWT 校验 + 游客识别"""
import uuid
from datetime import datetime, timedelta, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from config import settings
from utils.jwt_helper import verify_token

PUBLIC_PATHS = {
    "/health",
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/guest",
    "/api/cities",
    "/api/weather",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # 公开路径直接放行
        if any(path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        request.state.user_id = None
        request.state.is_guest = True
        request.state.guest_id = None

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = verify_token(token)
            if payload:
                request.state.user_id = payload.get("sub")
                request.state.is_guest = False

        # 没有游客ID则分配一个（用 X-Guest-Id 头或新生成）
        if request.state.is_guest:
            request.state.guest_id = request.headers.get(
                "X-Guest-Id", str(uuid.uuid4())
            )

        return await call_next(request)
