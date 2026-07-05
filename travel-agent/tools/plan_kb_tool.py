"""Tool: read_plan_knowledge_base — 读取标准化路书知识库"""
import json
from core.tool_registry import ToolExecutor, ToolDefinition
from repository.backend_proxy import backend_proxy


class PlanKBTool(ToolExecutor):
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="read_plan_knowledge_base",
            description="读取指定城市的标准化路书知识库，包括景点、建议时段、温馨提示",
            parameters={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"},
                    "section": {
                        "type": "string",
                        "description": "可选，指定天数如 day1，不填返回全部",
                    },
                },
                "required": ["city"],
            },
            max_calls_per_request=1,
        )

    async def execute(self, arguments: dict) -> str:
        city = arguments.get("city", "")
        if not city:
            return '{"error": "缺少 city 参数"}'

        plan = await backend_proxy.get_plan(city)
        # 限制返回长度
        text = json.dumps(plan, ensure_ascii=False)
        if len(text) > 2000:
            text = text[:2000] + "...(截断)"
        return text


plan_kb_tool = PlanKBTool()
