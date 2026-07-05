"""Tool: get_current_weather — 获取实时天气"""
from core.tool_registry import ToolExecutor, ToolDefinition
from repository.backend_proxy import backend_proxy


class WeatherTool(ToolExecutor):
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_current_weather",
            description="获取指定城市的实时天气数据，包括温度、天气状况、湿度、风力",
            parameters={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，如 北京"},
                },
                "required": ["city"],
            },
            max_calls_per_request=1,
        )

    async def execute(self, arguments: dict) -> str:
        city = arguments.get("city", "")
        if not city:
            return '{"error": "缺少 city 参数"}'
        import json
        weather = await backend_proxy.get_weather(city)
        return json.dumps(weather, ensure_ascii=False)


weather_tool = WeatherTool()
