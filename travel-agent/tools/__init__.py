"""工具包初始化 — 注册所有内置工具"""
from core.tool_registry import tool_registry
from .weather_tool import weather_tool
from .poi_tool import poi_tool
from .plan_kb_tool import plan_kb_tool


def register_all_tools():
    tool_registry.register(weather_tool)
    tool_registry.register(poi_tool)
    tool_registry.register(plan_kb_tool)


register_all_tools()
