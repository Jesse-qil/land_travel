"""预扣风控 — 第一层防线"""
from datetime import datetime, date
from pydantic import BaseModel
from config import settings


class CostGuardResult(BaseModel):
    allowed: bool
    reason: str = ""
    remaining_today: int = 0


class CostGuard:
    def __init__(self):
        self._daily_cost: float = 0.0
        self._daily_count_user: dict[str, int] = {}
        self._daily_count_ip: dict[str, int] = {}
        self._current_date: str = ""

    def _check_date_reset(self):
        today = date.today().isoformat()
        if today != self._current_date:
            self._current_date = today
            self._daily_cost = 0.0
            self._daily_count_user.clear()
            self._daily_count_ip.clear()

    async def check(self, user_id: str | None, client_ip: str) -> CostGuardResult:
        self._check_date_reset()

        if self._daily_cost >= settings.AI_DAILY_BUDGET:
            return CostGuardResult(
                allowed=False,
                reason="AI 服务今日费用已达上限，明日 0 点自动恢复",
                remaining_today=0,
            )

        if user_id:
            count = self._daily_count_user.get(user_id, 0)
            if count >= settings.AI_USER_DAILY_LIMIT:
                return CostGuardResult(
                    allowed=False,
                    reason=f"今日 AI 次数已用完（{settings.AI_USER_DAILY_LIMIT} 次/天）",
                )
            remaining = settings.AI_USER_DAILY_LIMIT - count
        else:
            count = self._daily_count_ip.get(client_ip, 0)
            if count >= settings.AI_GUEST_DAILY_LIMIT:
                return CostGuardResult(
                    allowed=False,
                    reason=f"游客今日 AI 次数已用完（{settings.AI_GUEST_DAILY_LIMIT} 次/天）",
                )
            remaining = settings.AI_GUEST_DAILY_LIMIT - count

        return CostGuardResult(allowed=True, remaining_today=remaining)

    def record_usage(
        self,
        user_id: str | None,
        client_ip: str,
        tokens_in: int,
        tokens_out: int,
        cost: float,
    ) -> None:
        self._check_date_reset()
        self._daily_cost += cost
        if user_id:
            self._daily_count_user[user_id] = self._daily_count_user.get(user_id, 0) + 1
        else:
            self._daily_count_ip[client_ip] = self._daily_count_ip.get(client_ip, 0) + 1

    def daily_cost(self) -> float:
        self._check_date_reset()
        return self._daily_cost


cost_guard = CostGuard()
