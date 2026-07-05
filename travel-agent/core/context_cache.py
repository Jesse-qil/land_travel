"""短时上下文缓存（多轮问答用）"""
import time
import uuid
from config import settings


class ContextCache:
    def __init__(self, ttl: int | None = None, max_messages: int | None = None):
        self.ttl = ttl or settings.CONTEXT_TTL
        self.max_messages = max_messages or settings.CONTEXT_MAX_MESSAGES
        self._sessions: dict[str, dict] = {}

    def get_or_create(self, session_id: str | None) -> tuple[str, list[dict]]:
        now = time.time()
        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            if now - session["last_active"] < self.ttl:
                session["last_active"] = now
                return session_id, session["messages"]
            else:
                del self._sessions[session_id]

        new_id = session_id or f"sess_{uuid.uuid4().hex[:12]}"
        self._sessions[new_id] = {"messages": [], "last_active": now}
        return new_id, []

    def append(self, session_id: str, role: str, content: str) -> None:
        if session_id not in self._sessions:
            return
        session = self._sessions[session_id]
        session["messages"].append({"role": role, "content": content})
        if len(session["messages"]) > self.max_messages:
            # 保留 system prompt（如有）+ 最近 N 条
            session["messages"] = session["messages"][-self.max_messages :]
        session["last_active"] = time.time()

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def cleanup_expired(self) -> int:
        now = time.time()
        expired = [
            sid for sid, s in self._sessions.items()
            if now - s["last_active"] >= self.ttl
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)


context_cache = ContextCache()
