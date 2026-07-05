# Travel Agent — AI 智能模块（独立服务）

> 基于《陆地旅行智能推荐系统 v3.2》项目文档生成。独立部署的 AI Agent 服务，
> 由主项目后端（travel-app/backend）通过 HTTP 调用。

## 定位

- 独立部署的轻量化 AI 智能服务（非重型 Agent 框架）
- 保留轻量 ToolCall 真实智能，舍弃 LangChain 等重型依赖
- 全程异步 LLM 调用，不阻塞主项目
- 预扣式成本风控，杜绝账单爆炸

## 目录结构

```
travel-agent/
├── server.py                 # FastAPI 服务入口
├── config.py                 # 配置管理
├── requirements.txt
├── .env.example
├── core/
│   ├── __init__.py
│   ├── llm_client.py         # DeepSeek 异步客户端
│   ├── tool_registry.py      # 工具注册表 + 调度
│   ├── output_validator.py   # 输出双层校验
│   ├── context_cache.py      # 短时上下文缓存
│   └── cost_guard.py         # 预扣风控
├── tools/                    # 工具实现
│   ├── __init__.py
│   ├── weather_tool.py       # 获取实时天气
│   ├── poi_tool.py           # 获取景点 POI 状态
│   └── plan_kb_tool.py       # 读取路书知识库
├── prompts/                  # 提示词模板
│   ├── plan_generation.txt
│   └── travel_qa.txt
├── repository/               # 数据访问层（Agent 不直连数据源，通过此层调主项目）
│   ├── __init__.py
│   └── backend_proxy.py      # 代理调用主项目 API
└── tests/
    └── __init__.py
```

## 对外接口

| 接口 | 方法 | 说明 |
|---|---|---|
| `/agent/plan` | POST | AI 智能行程生成（ToolCall） |
| `/agent/ask` | POST | AI 多轮问答（上下文缓存） |
| `/health` | GET | 健康检查 |

## 与主项目关系

```
用户 → 主项目 FastAPI(8000) → HTTP → Agent 服务(8001) → DeepSeek API
                                          ↓
                                  工具调用（通过 backend_proxy 反查主项目数据）
```
