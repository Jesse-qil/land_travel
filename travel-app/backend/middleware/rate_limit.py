"""限流中间件：IP / 用户级限流（简化版，基于内存计数）"""
import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, window: int = 60, max_requests: int = 60):
        super().__init__(app)
        self.window = window
        self.max_requests = max_requests
        self.counter: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        history = self.counter[client_ip]
        # 清理过期记录
        self.counter[client_ip] = [t for t in history if now - t < self.window]
        if len(self.counter[client_ip]) >= self.max_requests:
            from schemas.common import fail, ErrorCodes
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content=fail(ErrorCodes.RATE_LIMITED, "请求过于频繁，请稍后再试"),
            )
        self.counter[client_ip].append(now)
        return await call_next(request)
