"""工具注册表 + 调度器"""
from abc import ABC, abstractmethod
from pydantic import BaseModel


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: dict
    max_calls_per_request: int = 1


class ToolExecutor(ABC):
    @abstractmethod
    def definition(self) -> ToolDefinition: ...

    @abstractmethod
    async def execute(self, arguments: dict) -> str:
        """执行工具，返回 JSON 字符串结果"""


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolExecutor] = {}
        self._call_counts: dict[str, int] = {}

    def register(self, executor: ToolExecutor) -> None:
        name = executor.definition().name
        self._tools[name] = executor

    def get_all_definitions(self) -> list[dict]:
        result = []
        for executor in self._tools.values():
            defn = executor.definition()
            result.append({
                "type": "function",
                "function": {
                    "name": defn.name,
                    "description": defn.description,
                    "parameters": defn.parameters,
                },
            })
        return result

    async def dispatch(self, tool_name: str, arguments: dict) -> str:
        executor = self._tools.get(tool_name)
        if not executor:
            return f'{{"error": "未知工具: {tool_name}"}}'

        max_calls = executor.definition().max_calls_per_request
        count = self._call_counts.get(tool_name, 0)
        if count >= max_calls:
            return f'{{"error": "工具 {tool_name} 已达调用上限"}}'

        self._call_counts[tool_name] = count + 1
        try:
            return await executor.execute(arguments)
        except Exception as e:
            return f'{{"error": "工具执行失败: {e}"}}'

    def reset_call_counts(self) -> None:
        self._call_counts.clear()


tool_registry = ToolRegistry()
