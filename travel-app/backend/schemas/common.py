"""统一响应模型"""
from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: T | None = None


class ErrorCodes:
    SUCCESS = 0
    PARAM_ERROR = 1001
    UNAUTHORIZED = 1002
    RATE_LIMITED = 1003
    AI_UNAVAILABLE = 1004
    AUTH_ERROR = 1005
    VERSION_CONFLICT = 1006
    NOT_FOUND = 2001
    INTERNAL_ERROR = 5000


def ok(data: Any = None, message: str = "ok") -> dict:
    return {"code": ErrorCodes.SUCCESS, "message": message, "data": data}


def fail(code: int, message: str, data: Any = None) -> dict:
    return {"code": code, "message": message, "data": data}
