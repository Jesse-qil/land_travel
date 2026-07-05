"""认证路由：邮箱登录/注册/游客会话"""
import uuid
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request
from supabase import create_client

from schemas.common import ok, fail, ErrorCodes
from schemas.user import LoginRequest, RegisterRequest
from config import settings

router = APIRouter()

SUPABASE_CONFIGURED = bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY)

if SUPABASE_CONFIGURED:
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    except Exception:
        SUPABASE_CONFIGURED = False
        supabase = None


def _sign_jwt(user_id: str, is_guest: bool = False) -> str:
    payload = {
        "sub": user_id,
        "is_guest": is_guest,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


async def _create_profile(user_id: str, nickname: str):
    try:
        supabase.table("profiles").upsert({
            "id": user_id,
            "nickname": nickname,
            "avatar": "",
            "role": "user",
        }).execute()
    except Exception:
        pass


@router.post("/register")
async def register(req: RegisterRequest):
    """邮箱注册"""
    if not SUPABASE_CONFIGURED:
        return fail(
            ErrorCodes.AI_UNAVAILABLE,
            "邮箱注册尚未配置（Supabase Auth 未接入），请使用游客身份浏览",
        )
    try:
        resp = supabase.auth.sign_up({
            "email": req.email,
            "password": req.password,
        })
        if resp.user:
            await _create_profile(str(resp.user.id), req.nickname)
            token = _sign_jwt(str(resp.user.id))
            return ok({
                "token": token,
                "user": {"id": str(resp.user.id), "email": resp.user.email, "nickname": req.nickname},
            })
        return fail(ErrorCodes.AUTH_ERROR, "注册失败")
    except Exception as e:
        return fail(ErrorCodes.AUTH_ERROR, f"注册失败: {str(e)}")


@router.post("/login")
async def login(req: LoginRequest):
    """邮箱登录"""
    if not SUPABASE_CONFIGURED:
        return fail(
            ErrorCodes.AI_UNAVAILABLE,
            "邮箱登录尚未配置（Supabase Auth 未接入），请使用游客身份浏览",
        )
    try:
        resp = supabase.auth.sign_in_with_password({
            "email": req.email,
            "password": req.password,
        })
        if resp.user:
            token = _sign_jwt(str(resp.user.id))
            return ok({
                "token": token,
                "user": {"id": str(resp.user.id), "email": resp.user.email},
            })
        return fail(ErrorCodes.AUTH_ERROR, "登录失败")
    except Exception as e:
        return fail(ErrorCodes.AUTH_ERROR, f"登录失败: {str(e)}")


@router.get("/guest")
async def guest_session():
    """游客会话"""
    guest_id = f"guest_{uuid.uuid4().hex[:12]}"
    token = _sign_jwt(guest_id, is_guest=True)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
    return ok({"token": token, "guest_id": guest_id, "expires_at": expires_at.isoformat()})


@router.get("/me")
async def me(request: Request):
    """获取当前登录用户信息"""
    user_id = request.state.user_id
    if not user_id:
        return fail(ErrorCodes.UNAUTHORIZED, "未登录")
    
    if request.state.is_guest:
        return ok({"id": user_id, "is_guest": True, "nickname": "游客", "email": ""})
    
    try:
        resp = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if resp.data and len(resp.data) > 0:
            profile = resp.data[0]
            return ok({
                "id": profile.get("id", user_id),
                "is_guest": False,
                "nickname": profile.get("nickname", ""),
                "email": "",
            })
    except Exception:
        pass
    
    return ok({"id": user_id, "is_guest": False, "nickname": "", "email": ""})


@router.post("/logout")
async def logout(request: Request):
    """登出"""
    if SUPABASE_CONFIGURED and not request.state.is_guest:
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
    return ok(message="已登出")
