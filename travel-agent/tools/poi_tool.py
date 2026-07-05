"""Tool: check_poi_status — 查询景点 POI 实时状态

无真实数据源时返回 N/A，不编造景点开放状态。
"""
import json
from core.tool_registry import ToolExecutor, ToolDefinition


class POITool(ToolExecutor):
    """查询景点开放/限流状态

    说明：当前未接入高德 POI API 或主项目数据源，返回 N/A。
    接入后替换 execute 实现。
    """

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="check_poi_status",
            description="查询景点的实时开放、营业、限流状态",
            parameters={
                "type": "object",
                "properties": {
                    "spots": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "景点名称列表，最多 10 个",
                    },
                },
                "required": ["spots"],
            },
            max_calls_per_request=1,
        )

    async def execute(self, arguments: dict) -> str:
        spots = arguments.get("spots", [])
        if not spots:
            return '{"error": "缺少 spots 参数"}'
        if len(spots) > 10:
            return '{"error": "单次最多查询 10 个景点"}'

        # TODO: 接入高德 POI API 或主项目景点状态数据源
        # 当前无真实数据源，一律返回 N/A（不编造开放状态）
        result = {spot: "N/A" for spot in spots}
        result["_na_reason"] = "POI 实时状态数据源未接入"
        return json.dumps(result, ensure_ascii=False)


poi_tool = POITool()
