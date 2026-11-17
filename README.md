# fastapi-langchain-deepseek-chat-project

一个基于 **FastAPI + LangChain** 的「操作系统」答疑助手示例：对话模型使用 DeepSeek，会话历史持久化到 SQLite，支持多会话（`thread_id`），通过中间件在上下文变长时自动摘要压缩历史消息；同时内置 **RAG 知识库**——从操作系统 PDF 资料中检索相关内容，辅助模型回答专业问题。

## 功能

- `POST /chat` 对话接口，通过 `thread_id` 支持多会话
- `POST /clear` 清空指定会话的历史记录
- 对话模型使用 DeepSeek（`deepseek-chat`）
- 会话历史通过 LangGraph 的 `SqliteSaver` 持久化到本地 SQLite，服务重启后可继续对话
- 使用 `SummarizationMiddleware` 在消息数超阈值时自动摘要旧消息，控制上下文长度
- 摘要模型使用通义千问（通过 DashScope 的 OpenAI 兼容接口调用），输出简体中文摘要
- **RAG 知识库**：MinerU 解析操作系统 PDF → 递归切分 → DashScope 向量化 → Chroma 本地持久化；Agent 通过 `os_rag_search` 工具按需检索
- **系统提示词约束**：仅当问题与操作系统课程相关时才调用检索工具，其余问题直接用模型自身知识回答
- 使用 Pydantic 定义请求体（`Req`）

## 技术栈

| 组件 | 用途 |
| --- | --- |
| [FastAPI](https://fastapi.tiangolo.com/) | HTTP 服务 |
| [LangChain](https://python.langchain.com/) | Agent 构建、工具、中间件 |
| [LangGraph](https://langchain-ai.github.io/langgraph/) | 状态图与 checkpoint 持久化 |
| [langgraph-checkpoint-sqlite](https://pypi.org/project/langgraph-checkpoint-sqlite/) | SQLite checkpointer |
| [langchain-deepseek](https://pypi.org/project/langchain-deepseek/) | DeepSeek 模型接入 |
| [langchain-openai](https://python.langchain.com/docs/integrations/chat/openai/) | 通过 OpenAI 兼容接口接入通义千问 |
| DeepSeek `deepseek-chat` | 对话模型 |
| 通义千问 `qwen3.8-flash` | 摘要模型（DashScope OpenAI 兼容接口） |
| [langchain-mineru](https://pypi.org/project/langchain-mineru/) / MinerU | 解析 PDF 文档（支持扫描件 OCR） |
| [langchain-text-splitters](https://pypi.org/project/langchain-text-splitters/) | 递归切分文档为 chunk |
| DashScope `text-embedding-v3` | 文本向量化（通过 `langchain-community` 的 `DashScopeEmbeddings`） |
| [langchain-chroma](https://pypi.org/project/langchain-chroma/) / Chroma | 向量库本地持久化与检索 |
| [uv](https://docs.astral.sh/uv/) | 依赖管理与运行 |

要求 **Python >= 3.13**。

## 目录结构

```
.
├── main.py                              # FastAPI 入口，定义 POST /chat 与 POST /clear
├── app/
│   ├── config.py                        # 加载 .env 环境变量、配置 PDF 资源路径
│   ├── schemas.py                       # Req（请求体，含 prompt 与 thread_id）
│   ├── prompts.py                       # 系统提示词 + 摘要提示词
│   ├── model_provider.py                # 初始化对话模型、摘要模型、向量化模型
│   ├── agent/
│   │   └── agent_service.py             # create_agent 组装 Agent（含 RAG 检索工具）
│   ├── memory/
│   │   ├── langgraph_sqlite_memory.py   # SqliteSaver checkpointer
│   │   ├── session_manager.py           # 会话管理（清空指定 thread_id）
│   │   ├── summarize_middleware.py      # 摘要中间件配置
│   │   └── checkpoint.db                # 会话历史数据库（运行时生成）
│   └── rag/
│       ├── loader.py                    # 用 MinerU 加载 PDF 为 Document
│       ├── splitter.py                  # 递归切分 Document 为 chunk
│       ├── vector_store.py              # 构建 / 加载 Chroma 向量库
│       ├── retrieve_tool.py             # os_rag_search 检索工具
│       └── chroma_db/                   # 本地向量库持久化目录
├── resources/
│   └── 操作系统{1,2,3}.pdf               # RAG 知识库源文档
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

# 通义千问（DashScope）：摘要模型 + 向量化模型
DASHSCOPE_API_KEY=你的_dashscope_key
DASHSCOPE_BASE_URL=你的_dashscope_兼容接口地址

# MinerU：解析 PDF
MINERU_TOKEN=你的_mineru_token

# Chroma 向量库持久化路径（绝对路径）
CHROMA_ABSOLUTE_PATH=/path/to/chroma_db
```

| 变量 | 说明 |
| --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek 平台 API Key，用于对话模型 |
| `DASHSCOPE_API_KEY` | 阿里云百炼 / DashScope API Key，用于摘要模型与向量化模型 |
| `DASHSCOPE_BASE_URL` | DashScope 的 OpenAI 兼容接口地址，作为 `base_url` 传给摘要模型 |
| `MINERU_TOKEN` | MinerU API Token，用于解析 PDF 文档 |
| `CHROMA_ABSOLUTE_PATH` | Chroma 向量库的本地持久化目录（绝对路径） |

`.env` 已在 `.gitignore` 中忽略，不会被提交。

### 3. 构建 RAG 向量知识库

`app/rag/retrieve_tool.py` 在**模块加载时**就会读取向量库，因此首次启动服务前需要先构建好 Chroma 向量库。三个脚本均可直接运行，从项目根目录执行完整构建：

```bash
uv run python -m app.rag.vector_store
```

该脚本会依次：用 MinerU 加载 `resources/` 下的 PDF → 递归切分 → 向量化并写入 `CHROMA_ABSOLUTE_PATH`。若想分步查看每一步结果，可分别运行：

```bash
uv run python -m app.rag.loader      # 解析 PDF，生成 Document
uv run python -m app.rag.splitter    # 切分 Document，生成 chunk
uv run python -m app.rag.vector_store # 构建向量库
```

> 源文件路径配置在 `app/config.py` 的 `pdf_list` 中（相对路径），请按实际运行方式调整。

### 4. 启动服务

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
  "prompt": "你好",
  "thread_id": "001"
}
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `prompt` | 是 | 用户提问内容，长度 1 ~ 4096 字符 |
| `thread_id` | 否 | 会话主键，默认 `"001"`，长度 1 ~ 10 字符。不同 `thread_id` 对应不同的独立会话 |

**请求示例**

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "你好", "thread_id": "001"}'
```

**响应**

接口直接返回 `agent.invoke()` 的结果，主要字段：

| 字段 | 说明 |
| --- | --- |
| `messages` | 当前会话的完整消息列表（含历史与本次新增） |

本次回复的文本在消息列表最后一条 `AIMessage` 的 `content` 中。

### `POST /clear`

清空指定会话的全部历史记录（删除该 `thread_id` 在 SQLite 中的 checkpoint）。

**请求示例**

```bash
curl -X POST "http://127.0.0.1:8000/clear?thread_id=001"
```

**响应**

```json
{
  "ok": true,
  "message": "会话 001 已清除"
}
```

## 工作原理

1. `main.py` 收到 `prompt` 与 `thread_id`，包装成 `HumanMessage`，以 `thread_id` 作为会话主键交给 Agent。
2. `app/agent/agent_service.py` 通过 `create_agent` 组装：对话模型、系统提示词、checkpointer、摘要中间件、RAG 检索工具 `os_rag_search`。
3. checkpointer 依据 `thread_id` 从 SQLite 恢复该会话的历史消息。
4. 根据系统提示词，只有当问题与**操作系统**课程相关时才调用 `os_rag_search`：从 Chroma 向量库检索相关 PDF 片段并返回给模型作为参考；无关问题则直接由模型自身知识回答。
5. 调用模型前，`SummarizationMiddleware` 检查消息条数；达到阈值就把较早的消息交给摘要模型压缩成一段摘要，替换掉原文。
6. 模型结合检索结果（如有）产出回复，追加到消息列表。
7. 更新后的状态写回 SQLite。
8. 调用 `POST /clear` 时，`session_manager.clear_thread` 删除该 `thread_id` 的 checkpoint，会话从头开始。

## RAG 知识库

### 系统提示词与检索工具

系统提示词定义在 `app/prompts.py` 的 `system_prompt`，将 Agent 定位为「操作系统答疑助手」，并约定：

1. 只有问题与操作系统课程内容、概念、算法、调度、内存、文件系统等相关时，才调用 `os_rag_search` 查询知识库。
2. 与操作系统无关的问题直接用自身知识回答，**禁止调用检索工具**。
3. 使用检索资料回答时尽量贴合原文，不编造知识点。
4. 检索结果不足时如实说明，不强行编造。

检索工具 `os_rag_search` 定义在 `app/rag/retrieve_tool.py`：把向量库转为检索器（`k=5`），检索到的文档 `page_content` 拼接后作为工具返回值。

### 关键参数

| 环节 | 文件 | 参数 |
| --- | --- | --- |
| PDF 解析 | `app/rag/loader.py` | MinerU `mode="precision"`，`ocr=True`（支持扫描件） |
| 文本切分 | `app/rag/splitter.py` | `chunk_size=800`，`chunk_overlap=120`，分隔符 `\n\n`、`\n`、`。`、`，` |
| 向量化 | `app/model_provider.py` | DashScope `text-embedding-v3` |
| 向量检索 | `app/rag/retrieve_tool.py` | `k=5` |

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

由于一轮对话产生 **2 条**消息（`HumanMessage` + `AIMessage`），按此推算，从空会话开始，**首次压缩约发生在第 10 轮对话**；压缩后会话约剩 5~7 条消息，之后大约每 6~7 轮触发一次（具体取决于每次压缩后实际保留的条数）。

摘要提示词在 `app/prompts.py` 的 `summary_prompt` 中定义。其中 `{messages}` 是占位符，中间件会把对话记录填入该位置；缺少这个占位符会导致摘要模型收不到对话内容。

压缩是**替换式**的：被总结的原始消息会从当前会话状态中移除，只在摘要中保留信息。

## 数据存储

- 会话历史：`app/memory/checkpoint.db`（相对项目根目录）
- RAG 向量库：`CHROMA_ABSOLUTE_PATH` 指定的目录（仓库内已包含一份 `app/rag/chroma_db/` 示例数据）
- 请从项目根目录启动服务，否则会话数据库路径会失效、新建空库
- 会话数据库包含完整聊天记录，建议不要提交到版本库

## 当前实现的限制

- `thread_id` 由客户端传入（默认 `"001"`），但没有会话鉴权，任何请求都可以读写任意会话。
- `main.py` 在 `async` 路由中调用同步的 `agent.invoke()`，会阻塞事件循环；高并发场景建议改为 `await agent.ainvoke(...)`。
- `SqliteSaver` 使用单个 SQLite 连接（`check_same_thread=False`），不适合多进程部署（如 uvicorn 多 worker）。
- 会话数据库路径为相对路径，依赖启动时的工作目录。
- `app/config.py` 中的 `pdf_list` 使用相对路径，PDF 解析脚本依赖运行工作目录，换目录运行需调整路径。
- 向量库在服务启动时即加载；若 `CHROMA_ABSOLUTE_PATH` 为空或向量库未构建，检索工具会失败。
- 系统提示词把 Agent 限定为「操作系统答疑助手」，非操作系统问题虽可直接回答，但回答风格仍受该角色设定约束。

## License

[MIT](LICENSE)
