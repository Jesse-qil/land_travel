"""输出双层校验器"""
import json
import re
from pydantic import BaseModel


class ValidationResult(BaseModel):
    is_valid: bool
    data: dict | None = None
    errors: list[str] = []
    warnings: list[str] = []


FORBIDDEN_WORDS = ["违禁词示例"]


class OutputValidator:
    def validate(self, raw_output: str, expected_schema: dict | None = None) -> ValidationResult:
        errors, warnings = [], []

        data = self._try_parse_json(raw_output, errors)
        if data is None:
            return ValidationResult(is_valid=False, errors=errors)

        if expected_schema:
            for field in expected_schema.get("required", []):
                if field not in data:
                    errors.append(f"缺少必填字段: {field}")

        if "items" in data:
            for i, day in enumerate(data["items"]):
                if "day" not in day:
                    warnings.append(f"第 {i+1} 项缺少 day 字段")
                spots = day.get("spots", [])
                for j, spot in enumerate(spots):
                    if "name" not in spot:
                        warnings.append(f"第 {i+1} 天第 {j+1} 个景点缺少 name")
                    if "time" not in spot:
                        warnings.append(f"{spot.get('name', '?')} 缺少 time")

        content_str = json.dumps(data, ensure_ascii=False)
        for word in FORBIDDEN_WORDS:
            if word in content_str:
                errors.append(f"命中违禁词: {word}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            data=data if not errors else None,
            errors=errors,
            warnings=warnings,
        )

    def _try_parse_json(self, raw: str, errors: list[str]) -> dict | None:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        fixed = self._auto_fix_json(raw)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError as e:
            errors.append(f"JSON 解析失败: {e}")
            return None

    def _auto_fix_json(self, raw: str) -> str:
        # 提取代码块内容
        match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", raw)
        if match:
            return match.group(1)

        # 截取第一个 { 到最后一个 }
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            return raw[start : end + 1]

        return raw


output_validator = OutputValidator()
