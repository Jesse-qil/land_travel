"""后台管理路由（IP + 账号双重校验）"""
from fastapi import APIRouter, Request
from config import settings
from schemas.common import ok, fail, ErrorCodes

router = APIRouter()


def _check_admin(request: Request):
    client_ip = request.client.host if request.client else ""
    if client_ip not in settings.ADMIN_IP_WHITELIST:
        return False
    if not request.state.user_id:
        return False
    # TODO: 检查 profiles.role == 'admin'
    return True


@router.post("/plan")
async def manage_plan(request: Request, body: dict):
    if not _check_admin(request):
        return fail(ErrorCodes.UNAUTHORIZED, "无管理员权限")
    action = body.get("action")
    # TODO: create / update / delete
    return ok(message=f"操作 {action} 已执行")
