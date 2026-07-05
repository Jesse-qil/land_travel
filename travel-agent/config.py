"""Agent 服务配置"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PORT: int = int(os.getenv("AGENT_PORT", "8001"))

    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", "30"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1024"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))

    MAX_TOOL_ROUNDS: int = int(os.getenv("MAX_TOOL_ROUNDS", "3"))

    AI_DAILY_BUDGET: float = float(os.getenv("AI_DAILY_BUDGET", "30"))
    AI_GUEST_DAILY_LIMIT: int = int(os.getenv("AI_GUEST_DAILY_LIMIT", "5"))
    AI_USER_DAILY_LIMIT: int = int(os.getenv("AI_USER_DAILY_LIMIT", "10"))

    CONTEXT_TTL: int = int(os.getenv("CONTEXT_TTL", "600"))
    CONTEXT_MAX_MESSAGES: int = int(os.getenv("CONTEXT_MAX_MESSAGES", "20"))

    PLAN_CACHE_TTL: int = int(os.getenv("PLAN_CACHE_TTL", "3600"))

    BACKEND_BASE_URL: str = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
    BACKEND_SERVICE_TOKEN: str = os.getenv("BACKEND_SERVICE_TOKEN", "dev-service-token")


settings = Settings()
