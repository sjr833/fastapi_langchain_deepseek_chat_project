# fastapi-langchain-deepseek-chat-project

一个基于 **FastAPI + LangChain** 的 AI 聊天服务示例：使用 DeepSeek 作为对话模型，会话历史持久化到 SQLite，并通过中间件在上下文变长时自动生成摘要、压缩历史消息。

## 功能

- `POST /chat` 单一对话接口
- 对话模型使用 DeepSeek（`deepseek-chat`）
- 会话历史通过 LangGraph 的 `SqliteSaver` 持久化到本地 SQLite，服务重启后可继续对话
- 使用 `SummarizationMiddleware` 在消息数超阈值时自动摘要旧消息，控制上下文长度
- 摘要模型使用通义千问（通过 DashScope 的 OpenAI 兼容接口调用），输出简体中文摘要
- 使用 Pydantic 定义请求体（`Req`）与结构化输出格式（`Resp`）

## 技术栈

| 组件 | 用途 |
| --- | --- |
| [FastAPI](https://fastapi.tiangolo.com/) | HTTP 服务 |
| [LangChain](https://python.langchain.com/) | Agent 构建、中间件、结构化输出 |
| [LangGraph](https://langchain-ai.github.io/langgraph/) | 状态图与 checkpoint 持久化 |
| [langgraph-checkpoint-sqlite](https://pypi.org/project/langgraph-checkpoint-sqlite/) | SQLite checkpointer |
| [langchain-deepseek](https://pypi.org/project/langchain-deepseek/) | DeepSeek 模型接入 |
| DeepSeek `deepseek-chat` | 对话模型 |
| 通义千问 `qwen3.8-flash` | 摘要模型（DashScope OpenAI 兼容接口） |
| [uv](https://docs.astral.sh/uv/) | 依赖管理与运行 |

要求 **Python >= 3.13**。

## 目录结构

```
.
├── main.py                              # FastAPI 入口，定义 POST /chat
├── app/
│   ├── config.py                        # 加载 .env、定义会话 thread_id
│   ├── schemas.py                       # Req（请求体）/ Resp（结构化输出）
│   ├── prompts.py                       # 系统提示词 + 摘要提示词
│   ├── model_provider.py                # 初始化对话模型与摘要模型
│   ├── agent/
│   │   └── agent_service.py             # create_agent 组装 Agent
│   └── memory/
│       ├── langgraph_sqlite_memory.py   # SqliteSaver checkpointer
│       └── summarize_middleware.py      # 摘要中间件配置
├── pyproject.toml                       # 依赖声明
├── uv.lock                              # 依赖锁定
└── LICENSE                              # MIT
```

## 快速开始

### 1. 克隆并安装依赖

```bash
git clone git@github.com:sjr833/fastapi_langchain_deepseek_chat_project.git
cd fastapi_langchain_deepseek_chat_project
uv sync
```

> `pyproject.toml` 中已配置清华 PyPI 镜像为默认源。

### 2. 配置环境变量

在项目根目录创建 `.env`：

```dotenv
# DeepSeek
DEEPSEEK_API_KEY=你的_deepseek_key

# 通义千问（DashScope）
DASHSCOPE_API_KEY=你的_dashscope_key
DASHSCOPE_BASE_URL=你的_dashscope_兼容接口地址
```

| 变量 | 说明 |
| --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek 平台 API Key，用于对话模型 |
| `DASHSCOPE_API_KEY` | 阿里云百炼 / DashScope API Key，用于摘要模型 |
| `DASHSCOPE_BASE_URL` | DashScope 的 OpenAI 兼容接口地址，作为 `base_url` 传给 `init_chat_model` |

`.env` 已在 `.gitignore` 中忽略，不会被提交。

### 3. 启动服务

```bash
uv run python main.py
```

默认监听 `0.0.0.0:8000`，开启 `reload`。也可以用：

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API

### `POST /chat`

**请求体**

```json
{
  "prompt": "你好"
}
```

`prompt` 为必填，长度 1 ~ 4096 字符。

**请求示例**

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "你好"}'
```

**响应**

接口直接返回 `agent.invoke()` 的结果，主要字段：

| 字段 | 说明 |
| --- | --- |
| `messages` | 当前会话的完整消息列表（含历史与本次新增） |
| `structured_response.content` | 本次回复的文本内容 |

> 由于 Agent 使用 `response_format=Resp` 的结构化输出，模型回复通过工具调用返回：`AIMessage.content` 为空，真实文本在 `AIMessage.tool_calls[0].args.content` 与随后的 `ToolMessage.content` 中。取回复文本请优先使用 `structured_response.content`。

## 工作原理

1. `main.py` 收到 `prompt`，包装成 `HumanMessage` 交给 Agent。
2. `app/agent/agent_service.py` 通过 `create_agent` 组装：对话模型、系统提示词、结构化输出格式、checkpointer、摘要中间件。
3. checkpointer 依据 `thread_id` 从 SQLite 恢复该会话的历史消息。
4. 调用模型前，`SummarizationMiddleware` 检查消息条数；达到阈值就把较早的消息交给摘要模型压缩成一段摘要，替换掉原文。
5. 模型产出 `tool_call`，框架解析成 `Resp` 对象，并补一条 `ToolMessage` 记录返回内容。
6. 更新后的状态写回 SQLite。

## 会话压缩行为

相关配置在 `app/memory/summarize_middleware.py`：

```python
SummarizationMiddleware(
    model=model_summarize,
    trigger=("messages", 20),
    keep=("messages", 4),
    summary_prompt=summary_prompt,
)
```

| 参数 | 值 | 含义 |
| --- | --- | --- |
| `trigger` | `("messages", 20)` | 消息数达到 20 条时触发压缩 |
| `keep` | `("messages", 4)` | 压缩后保留最近 4 条原始消息 |

由于使用了结构化输出，一轮对话会产生 **3 条**消息（`HumanMessage` + 空内容的 `AIMessage` + `ToolMessage`）。按此推算，从空会话开始，**首次压缩约发生在第 8 轮对话**；压缩后会话约剩 5~7 条消息，之后大约每 5 轮触发一次（具体取决于每次压缩后实际保留的条数）。

摘要提示词在 `app/prompts.py` 的 `summary_prompt` 中定义。其中 `{messages}` 是占位符，中间件会把对话记录填入该位置；缺少这个占位符会导致摘要模型收不到对话内容。

压缩是**替换式**的：被总结的原始消息会从当前会话状态中移除，只在摘要中保留信息。

## 数据存储

- 数据库文件：`app/memory/checkpoint.db`（相对项目根目录）
- 请从项目根目录启动服务，否则会新建一个空数据库
- 该文件包含完整聊天记录，建议不要提交到版本库

## 当前实现的限制

- `app/config.py` 中的 `thread_id` 固定为 `thread_1`，所有请求共享同一个会话。如需多用户/多会话，需要为每个请求传入独立 `thread_id`。
- `main.py` 在 `async` 路由中调用同步的 `agent.invoke()`，会阻塞事件循环；高并发场景建议改为 `await agent.ainvoke(...)`。
- `SqliteSaver` 使用单个 SQLite 连接（`check_same_thread=False`），不适合多进程部署（如 uvicorn 多 worker）。
- 数据库路径为相对路径，依赖启动时的工作目录。

## License

[MIT](LICENSE)
