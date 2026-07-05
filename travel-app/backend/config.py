"""环境变量与配置管理"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "陆地旅行智能推荐系统")
    VERSION: str = os.getenv("VERSION", "3.2.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:4173"
    ).split(",")

    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")

    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    JWT_ALG: str = "HS256"

    QWEATHER_API_KEY: str = os.getenv("QWEATHER_API_KEY", "")
    QWEATHER_BASE: str = os.getenv("QWEATHER_BASE", "https://devapi.qweather.com")

    AMAP_API_KEY: str = os.getenv("AMAP_API_KEY", "")

    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    AI_DAILY_BUDGET: float = float(os.getenv("AI_DAILY_BUDGET", "30"))
    AI_GUEST_DAILY_LIMIT: int = int(os.getenv("AI_GUEST_DAILY_LIMIT", "5"))
    AI_USER_DAILY_LIMIT: int = int(os.getenv("AI_USER_DAILY_LIMIT", "10"))
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "1024"))

    ADMIN_IP_WHITELIST: list[str] = os.getenv(
        "ADMIN_IP_WHITELIST", "127.0.0.1"
    ).split(",")

    DATA_DIR: Path = BASE_DIR / "data"

    AGENT_BASE_URL: str = os.getenv("AGENT_BASE_URL", "http://localhost:8001")
    BACKEND_SERVICE_TOKEN: str = os.getenv("BACKEND_SERVICE_TOKEN", "dev-service-token")


settings = Settings()
