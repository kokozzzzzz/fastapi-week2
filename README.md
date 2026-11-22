# FastAPI Week 2

一个用于系统学习 FastAPI 的后端练习项目。项目从基础路由开始，逐步覆盖 Pydantic 数据校验、分层架构、MySQL 持久化、JWT 用户认证、文件上传、外部 API 调用、pytest 接口测试、Redis 缓存、Docker 容器化与 Docker Compose 编排，以及基于 DeepSeek 的 AI 问答、文本总结与信息提取接口（提示词模板化，支持少样本，问答支持 SSE 流式输出），最终形成一个结构清晰、可运行、可测试的 FastAPI 应用。

- 主应用入口：`app/main.py`
- 交互式接口文档：<http://127.0.0.1:8000/docs>
- 学习记录：见文末「开发日志」

## 技术栈

| 分类 | 技术 |
| --- | --- |
| 语言 | Python 3.13 |
| Web 框架 | FastAPI |
| 数据校验 / 配置 | Pydantic、pydantic-settings |
| ORM / 数据库 | SQLAlchemy 2.x、MySQL、PyMySQL |
| 缓存 | Redis、redis.asyncio |
| 认证 | JWT（PyJWT）、Argon2 密码哈希（pwdlib） |
| 外部请求 | httpx |
| 大模型 | OpenAI SDK（AsyncOpenAI）、DeepSeek API |
| 流式输出 | SSE（FastAPI 内置 `EventSourceResponse`） |
| 服务器 | Uvicorn |
| 容器化 | Docker、Docker Compose |
| 测试 | pytest、FastAPI TestClient |

## 功能

- **用户管理**：用户的增删改查与分页查询，数据持久化到 MySQL；用户名唯一，字段由 Pydantic 校验。
- **用户认证**：注册、登录、获取当前用户；密码使用 Argon2 哈希后入库，登录返回 JWT，受保护接口通过 `Authorization: Bearer <token>` 访问。
- **接口保护**：`/users` 路由整体挂载 `get_current_user` 依赖，未携带有效 token 的请求统一返回 401。
- **文件上传**：仅允许 `.txt` / `.md` / `.pdf`，单文件最大 5MB；文件以 UUID 重命名保存至 `uploads/`，原始文件名随响应返回。
- **外部 API**：通过 `httpx` 异步调用 GitHub 用户接口，返回精简后的公开信息，并映射 404 / 502 错误。
- **Redis 缓存**：基于 `redis.asyncio` 的异步客户端，支持缓存写入（60 秒 TTL）、读取、删除与 TTL 查询；`/cache/demo` 演示 Cache-Aside 模式。
- **用户详情缓存**：`GET /users/{user_id}` 采用 Cache-Aside，key 为 `user:{user_id}`，TTL 由 `USER_CACHE_TTL` 控制（默认 60 秒）；响应头 `X-Cache` 标记 `HIT` / `MISS`，更新或删除用户时自动使缓存失效。
- **AI 能力**：`POST /ai/chat` 问答、`POST /ai/summarize` 文本总结、`POST /ai/extract` 信息提取，统一通过 OpenAI SDK 异步调用 DeepSeek，返回回答文本与模型名；提示词集中在 `app/ai/prompts.py`，提取接口可切换零样本 / 少样本；未配置 API Key 或请求受限返回 503，请求超时返回 504，认证 / 连接 / 服务端错误返回 502。
- **流式问答（SSE）**：`POST /ai/chat/stream` 通过 Server-Sent Events 逐段推送回答，`delta` 事件携带增量文本，正常结束发送 `done`，异常发送 `error`；客户端断开后停止生成。
- **基础设施**：健康检查、请求耗时中间件（响应头 `X-Process-Time`）、CORS（允许 Vite 开发服务器跨域）。
- **自动化测试**：pytest + TestClient，使用独立测试数据库，覆盖认证、用户、文件上传、健康检查与提示词消息构造。

## 目录结构

```text
FastAPI-week2/
├── app/                          # 主应用
│   ├── main.py                   # 应用入口：创建 FastAPI 实例、注册中间件 / CORS / 路由、自动建表
│   ├── ai/                       # 大模型接入层
│   │   ├── client.py             # AsyncOpenAI 客户端（lru_cache 复用）、generate_answer() 与 stream_answer()
│   │   ├── prompts.py            # 系统提示词与消息构造：chat / summary / extract（含少样本）
│   │   ├── prompt_experiment.py  # temperature 对比实验脚本（独立运行，不参与应用）
│   │   └── llm_test.py           # DeepSeek 同步调用练习脚本（独立运行，不参与应用）
│   ├── api/                      # 路由层：只处理 HTTP 请求与响应
│   │   ├── ai.py                 # /ai 问答、文本总结、信息提取与 SSE 流式问答
│   │   ├── auth.py               # /auth 注册、登录、当前用户
│   │   ├── cache.py              # /cache 缓存读写与 Cache-Aside 演示
│   │   ├── external.py           # /external 调用 GitHub API
│   │   ├── files.py              # /files 文件上传
│   │   ├── health.py             # /health/ 健康检查
│   │   └── users.py              # /users 用户相关接口（整体需要登录，详情接口带缓存）
│   ├── cache/                    # 缓存层
│   │   ├── client.py             # 全局 redis.asyncio 客户端
│   │   └── user_cache.py         # 用户详情缓存：读取 / 写入 / 删除（key = user:{id}）
│   ├── core/                     # 基础设施层
│   │   ├── config.py             # Settings：从 .env 读取配置
│   │   ├── dependencies.py       # OAuth2PasswordBearer + get_current_user
│   │   ├── middleware.py         # 请求耗时中间件
│   │   └── security.py           # 密码哈希与 JWT 签发 / 校验
│   ├── db/                       # 数据库连接层
│   │   ├── base.py               # 声明基类 Base
│   │   └── session.py            # engine / SessionLocal / get_db 依赖
│   ├── models/
│   │   └── user.py               # User ORM 模型（含 password_hash），映射 users 表
│   ├── schemas/
│   │   ├── ai.py                 # ChatRequest / ChatResponse / TextRequest / ExtractRequest
│   │   ├── auth.py               # 登录 / Token 响应模型
│   │   └── user.py               # UserCreate / UserUpdate / UserResponse
│   └── services/                 # 业务逻辑层
│       ├── ai_service.py         # AI 业务：构造消息并调用大模型（chat / stream chat / summarize / extract）
│       ├── auth_service.py       # 注册与登录校验
│       └── user_service.py       # 用户增删改查
│
├── tests/                        # pytest 自动化测试
│   ├── conftest.py               # 测试数据库、TestClient、auth_headers fixture
│   ├── test_ai_prompts.py        # 提示词消息构造测试（不调用真实模型）
│   ├── test_auth.py              # 注册 / 登录 / 当前用户测试
│   ├── test_files.py             # 文件上传测试
│   ├── test_health.py            # 健康检查与参数校验测试
│   └── test_users.py             # 用户接口认证与查询测试
│
├── examples/
│   └── redis_demo.py             # Redis 基础操作练习脚本（独立运行，不参与应用）
│
├── conftest.py                   # 空文件，让 pytest 把项目根加入 sys.path
├── requirements.txt              # 固定版本的依赖清单
├── Dockerfile                    # 镜像构建文件（python:3.13-slim + uvicorn）
├── compose.yaml                  # Docker Compose 编排：MySQL + Redis + API 一键启动
├── .dockerignore                 # 构建上下文排除规则（.venv、.env、uploads 等）
├── .env_example                  # 环境变量模板（可提交）
├── .env                          # 本地私有配置（不提交）
├── uploads/                      # 上传文件保存目录（运行时自动创建，已忽略）
└── README.md
```

> **说明**：`app/db/` 与 `app/models/` 没有放置 `__init__.py`，依赖 Python 的命名空间包机制导入，目前可以正常工作；若想与其余目录保持一致，补两个空文件即可。

## 环境配置

### 1. 环境要求

- Python 3.13+
- MySQL（已启动，且可创建数据库）
- Redis（已启动，默认 `localhost:6379`）
- Git
- Docker + Docker Compose（可选，用于容器化 / 编排运行）

### 2. 克隆项目并安装依赖

```bash
git clone https://github.com/kokozzzzzz/fastapi-week2.git
cd fastapi-week2
```

创建并激活虚拟环境：

```bash
python -m venv .venv
```

Windows（CMD / PowerShell）：

```bash
.venv\Scripts\activate
```

Windows（Git Bash）：

```bash
source .venv/Scripts/activate
```

macOS / Linux：

```bash
source .venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制模板并填入真实值：

```bash
cp .env_example .env
```

```env
GITHUB_TOKEN=

APP_NAME=
DEBUG=

DATABASE_URL=
TEST_DATABASE_URL=

SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
USER_CACHE_TTL=60

# MySQL Docker Compose 配置
MYSQL_ROOT_PASSWORD=
MYSQL_DATABASE=
MYSQL_USER=
MYSQL_PASSWORD=

# 大语言模型配置
DEEPSEEK_API_KEY=
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-flash
LLM_TIMEOUT=60
```

| 变量 | 必填 | 说明 |
| --- | --- | --- |
| `GITHUB_TOKEN` | 是 | 调用 GitHub API 的 Token。`app/api/external.py` 在模块导入时读取，缺失会导致应用无法启动 |
| `APP_NAME` | 否 | 应用名称，显示在 Swagger 文档标题中，默认 `FastAPI Week 2` |
| `DEBUG` | 否 | 调试开关，默认 `true` |
| `DATABASE_URL` | 是 | 主数据库连接串，格式见下方「数据库初始化」 |
| `TEST_DATABASE_URL` | 运行测试时必填 | 测试数据库连接串，**必须与主数据库分开** |
| `SECRET_KEY` | 是 | JWT 签名密钥，没有默认值，建议使用足够长的随机字符串 |
| `ALGORITHM` | 否 | JWT 签名算法，默认 `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 否 | Token 有效期（分钟），默认 `30` |
| `REDIS_HOST` | 否 | Redis 主机，默认 `localhost` |
| `REDIS_PORT` | 否 | Redis 端口，默认 `6379` |
| `REDIS_DB` | 否 | Redis 逻辑数据库编号，默认 `0` |
| `USER_CACHE_TTL` | 否 | 用户详情缓存过期时间（秒），默认 `60` |
| `DEEPSEEK_API_KEY` | 调用 `/ai/chat` 时必填 | DeepSeek API Key。留空不影响应用启动，但调用 AI 接口会返回 503 |
| `LLM_BASE_URL` | 否 | OpenAI 兼容接口地址，默认 `https://api.deepseek.com` |
| `LLM_MODEL` | 否 | 调用的模型名称，默认 `deepseek-flash` |
| `LLM_TIMEOUT` | 否 | 调用大模型的超时时间（秒），默认 `60`；超时返回 504 |
| `MYSQL_ROOT_PASSWORD` | 使用 Docker Compose 时必填 | MySQL root 密码，供 Compose 初始化数据库与健康检查使用 |
| `MYSQL_DATABASE` | 使用 Docker Compose 时必填 | Compose 启动时自动创建的数据库名，同时用于拼接容器内 `DATABASE_URL` |
| `MYSQL_USER` | 使用 Docker Compose 时必填 | Compose 创建的 MySQL 用户，`api` 容器用它连接数据库 |
| `MYSQL_PASSWORD` | 使用 Docker Compose 时必填 | 上述 MySQL 用户的密码 |

生成一个随机 `SECRET_KEY`：

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

> **提示**：复制模板后不要保留空值。`DEBUG=` 留空时，pydantic 无法把空字符串解析为布尔值，应用会直接启动失败；不想配置的可选字段请删除对应行（`APP_NAME=` 留空只会得到空标题）。`GITHUB_TOKEN`、`DATABASE_URL`、`SECRET_KEY` 必须填写。

> **⚠️ 安全提示**：`.env` 中的 Token、数据库密码和 `SECRET_KEY` 等同于密码，不要提交到 Git。仓库的 `.gitignore` 已包含 `.env`；`.env_example` 只放变量名，不放真实值。

> **注意**：`SettingsConfigDict(env_file=".env")` 按**当前工作目录**解析路径，因此请在项目根目录启动服务，否则会读不到 `.env`。`SECRET_KEY` 没有默认值，缺失时应用会直接启动失败。

## 数据库初始化

### 1. 创建数据库

先启动 MySQL，然后创建主数据库和测试数据库：

```sql
CREATE DATABASE fastapi_week2 DEFAULT CHARACTER SET utf8mb4;
CREATE DATABASE fastapi_week2_test DEFAULT CHARACTER SET utf8mb4;
```

### 2. 配置连接串

在 `.env` 中填写（按实际用户名、密码、主机和端口修改）：

```env
DATABASE_URL=mysql+pymysql://root:your_password@127.0.0.1:3306/fastapi_week2
TEST_DATABASE_URL=mysql+pymysql://root:your_password@127.0.0.1:3306/fastapi_week2_test
```

### 3. 自动建表

应用启动时会执行 `Base.metadata.create_all(bind=engine)`，自动创建 `users` 表，不需要手写建表 SQL。

> **⚠️ 表结构变更注意**：`create_all()` 只创建缺失的表，**不会修改已存在的表**。如果数据库中已有旧版 `users` 表（例如 Day 4 创建、没有 `password_hash` 列），需要手动处理：
>
> ```sql
> ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT '';
> ```
>
> 已有用户补上空默认值后无法登录，需要重新注册或更新密码。也可以删表让应用重建，但会丢失已有数据。项目目前尚未接入 Alembic 迁移工具。

## Redis 缓存

### 1. 启动 Redis

本地需要先启动 Redis，默认连接 `localhost:6379`。Windows 可用 Docker Desktop、WSL 或 Memurai；Docker 方式：

```bash
docker run -d --name redis-dev -p 6379:6379 redis:7
```

连接参数在 `.env` 中通过 `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` 配置（见上方环境变量表）。

### 2. 客户端

`app/cache/client.py` 使用 `redis.asyncio.Redis` 创建全局异步客户端：

```python
redis_client = redis.Redis(
    host=setting.redis_host,
    port=setting.redis_port,
    db=setting.redis_db,
    decode_responses=True,
)
```

`decode_responses=True` 让 `get()` 直接返回字符串而不是 `bytes`。

### 3. 缓存接口

`app/api/cache.py` 提供一组练习接口：

- `/cache/test/{key}` 的 POST / GET / DELETE 分别写入、读取、删除缓存，写入固定 TTL 60 秒；POST 的 `value` 是**查询参数**，不是请求体。
- `GET /cache/test/{key}/ttl` 返回剩余过期时间：正数为剩余秒数，`-1` 表示永不过期，`-2` 表示 key 不存在。
- `GET /cache/demo` 演示 Cache-Aside 模式：首次请求用 `asyncio.sleep(2)` 模拟慢查询并写入 60 秒缓存，期间再次请求直接命中 Redis；响应中的 `source` 字段区分 `redis` 与 `slow source`。

> **注意**：Redis 客户端在模块导入时创建，但连接是惰性的——Redis 未启动时应用仍能启动，访问 `/cache/*` 或 `GET /users/{user_id}` 才会返回 500。`examples/redis_demo.py` 是独立的同步客户端练习脚本（`set` / `get` / `ex` / `ttl`），不参与应用运行。

### 4. 用户详情缓存

`app/cache/user_cache.py` 为 `GET /users/{user_id}` 提供 Cache-Aside 缓存：

- key 为 `user:{user_id}`，value 是包含 `id` / `name` / `age` 的 JSON 字符串，TTL 读取 `USER_CACHE_TTL`（默认 60 秒）。
- 命中缓存：直接返回缓存数据，响应头 `X-Cache: HIT`。
- 未命中：查询 MySQL，写入缓存后返回，响应头 `X-Cache: MISS`；用户不存在仍返回 404。
- 更新（`PUT`）或删除（`DELETE`）用户成功后调用 `delete_user_cache()` 使缓存失效。
- 绕过接口直接修改数据库不会同步缓存，最多读到 TTL 时间内的旧数据。

## AI 能力（DeepSeek）

### 1. 配置

在 `.env` 中填写 `DEEPSEEK_API_KEY`（调用 AI 接口时必填），其余变量有默认值，可按需覆盖：

```env
DEEPSEEK_API_KEY=sk-...
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-flash
LLM_TIMEOUT=60
```

`DEEPSEEK_API_KEY` 为空时应用仍能正常启动，调用 `POST /ai/chat` 会返回 503。

### 2. 实现结构

- `app/ai/prompts.py`：集中维护三组中文系统提示词，并提供对应的消息构造函数：
  - `build_chat_messages()`：问答，system + user 两条消息。
  - `build_summary_messages()`：总结，要求按「一句话概括 / 主要内容（3～5 个要点）/ 关键数据」的格式输出。
  - `build_extract_messages()`：信息提取，按「事项名称、时间、地点、组织方、面向对象、截止时间、联系方式」逐项提取，缺失字段填「未提及」；`use_few_shot=True` 时插入两组示例问答（共 6 条消息），否则只有 system + user 两条。
  - 总结与提取的提示词都用 `<待处理文本>` 标签包裹用户输入；提取提示词还声明标签内的内容不视为系统指令，用于降低提示词注入风险。
- `app/ai/client.py`：用 `lru_cache(maxsize=1)` 复用 `AsyncOpenAI` 客户端，`base_url` 指向 DeepSeek 的 OpenAI 兼容接口，超时读取 `LLM_TIMEOUT`，`max_retries=2`；`generate_answer(messages, temperature=None)` 调用 `chat.completions.create()`，校验 `choices` 与回答内容非空后，返回去除首尾空白的文本。传入 `temperature` 时校验范围 0–2，并通过 `extra_body` 关闭 DeepSeek 的 thinking 模式。`stream_answer(messages)` 以 `stream=True` 调用同一接口，逐段 `yield` 增量文本，跳过空 chunk，同样关闭 thinking 模式，并在 `finally` 中关闭流。
- `app/services/ai_service.py`：`chat_with_ai()` / `summarize_text()` / `extract_key_info()` 分别构造消息后调用 `generate_answer()`；总结与提取固定 `temperature=0.2`，问答使用模型默认值；`stream_chat_with_ai()` 复用问答消息构造，异步迭代 `stream_answer()`。
- `app/api/ai.py`：三个非流式接口共用 `_run_ai_task()`，将大模型异常统一映射为 HTTP 错误；流式接口在生成器内把异常转换为 `error` 事件（见下节）。

### 3. 接口

| Endpoint | 请求体 | 说明 |
| --- | --- | --- |
| `POST /ai/chat` | `{"message": "..."}` | 问答，`message` 1–4000 字符 |
| `POST /ai/summarize` | `{"text": "..."}` | 文本总结，`text` 1–8000 字符 |
| `POST /ai/extract` | `{"text": "...", "use_few_shot": false}` | 信息提取，`use_few_shot` 默认 `false` |
| `POST /ai/chat/stream` | `{"message": "..."}` | 流式问答（SSE），事件格式见下节 |

文本字段都会去除首尾空白，纯空白内容返回 422。三个非流式接口的成功响应统一为 `{"answer": "...", "model": "deepseek-flash"}`。

### 4. 流式问答（SSE）

`POST /ai/chat/stream` 使用 FastAPI 内置的 `EventSourceResponse` 返回 `text/event-stream`，请求体与 `/ai/chat` 相同（`ChatRequest`）。

服务端通过三类事件推送结果：

| event | data | 说明 |
| --- | --- | --- |
| `delta` | `{"type": "delta", "content": "..."}` | 模型输出的增量文本，可能连续多次 |
| `done` | `{"type": "done"}` | 正常结束标记 |
| `error` | `{"type": "error", "message": "..."}` | 模型异常，`message` 为错误说明 |

实际传输格式示例：

```text
event: delta
data: {"type":"delta","content":"FastAPI 是一个"}

event: delta
data: {"type":"delta","content":"现代 Python Web 框架。"}

event: done
data: {"type":"done"}
```

- 每段输出前都会检查 `request.is_disconnected()`，客户端断开后停止生成；此时不会发送 `done`。
- 流式接口的模型异常（限流、超时、连接失败、服务端错误、未配置 `DEEPSEEK_API_KEY`）不会返回 502 / 503 / 504——响应头在开始推送时已发出，HTTP 状态固定为 200，错误只体现在 `error` 事件里。请求体校验失败仍会在开始推送前返回 422。
- 流式问答使用模型默认 temperature，并关闭 DeepSeek 的 thinking 模式。
- 浏览器原生 `EventSource` 只支持 GET，请求该 POST 接口需使用 `fetch()` 读取响应流。

### 5. 错误映射

| 状态码 | 场景 |
| --- | --- |
| 422 | 请求文本为空、只有空白或超过长度限制 |
| 502 | API Key 认证失败、无法连接大模型服务、大模型返回错误状态码 |
| 503 | 未配置 `DEEPSEEK_API_KEY`、模型返回空回答，或请求受限 / 账户额度不足 |
| 504 | 请求大模型超时（默认 60 秒） |

> **注意**：上表适用于 `/ai/chat`、`/ai/summarize`、`/ai/extract`。`/ai/chat/stream` 在响应开始后无法再修改状态码，模型异常统一以 `error` 事件发送。

> **提示**：`app/ai/prompt_experiment.py` 会依次用 temperature 0.2 / 0.7 / 1.2 调用同一问题，对比输出差异，在项目根目录运行 `python -m app.ai.prompt_experiment`。`app/ai/llm_test.py` 是独立的同步调用练习脚本，在项目根目录运行 `python app/ai/llm_test.py` 可在终端交互测试 DeepSeek。两者都不参与应用运行。

## 运行方式

在**项目根目录**启动主应用：

```bash
uvicorn app.main:app --reload
```

如果 `uvicorn` 命令不可用，可以改用：

```bash
python -m uvicorn app.main:app --reload
```

默认监听 `http://127.0.0.1:8000`，`--reload` 表示代码变更后自动重启。

启动后可访问：

- Swagger UI：<http://127.0.0.1:8000/docs>
- ReDoc：<http://127.0.0.1:8000/redoc>

> **提示**：`/users/`、`/files/`、`/health/` 带结尾斜杠，请求不带斜杠的路径会收到 307 重定向；`/auth/...`、`/external/...`、`/cache/...`、`/ai/...` 不带结尾斜杠。

## Docker 容器化

### 1. Dockerfile

`Dockerfile` 基于 `python:3.13-slim` 构建镜像：

- 设置 `PYTHONDONTWRITEBYTECODE=1`（不生成 `.pyc`）与 `PYTHONUNBUFFERED=1`（日志实时输出）。
- 先复制 `requirements.txt` 安装依赖，再复制项目代码，代码改动时可以复用依赖层的构建缓存。
- `EXPOSE 8000`，启动命令为 `uvicorn app.main:app --host 0.0.0.0 --port 8000`。

`.dockerignore` 排除了 `.venv/`、`__pycache__/`、`.git/`、`.env`、`uploads/`、`.pytest_cache/` 等，避免把虚拟环境、密钥和运行时文件打进镜像。

### 2. 构建与运行

在项目根目录构建镜像：

```bash
docker build -t fastapi-week2 .
```

运行容器并通过 `--env-file` 注入环境变量：

```bash
docker run -d --name fastapi-week2 -p 8000:8000 --env-file .env fastapi-week2
```

启动后访问 <http://127.0.0.1:8000/docs>。查看日志、停止与删除容器：

```bash
docker logs -f fastapi-week2
docker stop fastapi-week2
docker rm fastapi-week2
```

### 3. 注意事项

- **环境变量必须运行时传入**：`.dockerignore` 排除了 `.env`，镜像内没有配置文件；缺少 `SECRET_KEY`、`GITHUB_TOKEN` 时应用会直接启动失败，因此必须使用 `--env-file .env` 或 `-e` 逐个传入。
- **容器内的 `localhost` 不是宿主机**：如果 MySQL / Redis 跑在宿主机上，`.env` 中的 `DATABASE_URL` 与 `REDIS_HOST` 要改为 `host.docker.internal`（Docker Desktop 在 Windows / macOS 上支持），否则容器内连不上。
- **镜像内不包含热重载**：`CMD` 未带 `--reload`，修改代码后需要重新 `docker build` 并重建容器。
- **上传文件不持久化**：容器内 `uploads/` 的文件随容器删除而丢失，需要时可挂载卷：`-v "$(pwd)/uploads:/app/uploads"`（Git Bash 写法；PowerShell 使用 `${PWD}/uploads:/app/uploads`）。使用 Docker Compose 时已自动挂载（见下一节）。

## Docker Compose 编排

`compose.yaml` 定义 `mysql`、`redis`、`api` 三个服务，用一条命令拉起完整运行环境。

### 1. 服务组成

| 服务 | 镜像 / 构建 | 端口映射 | 说明 |
| --- | --- | --- | --- |
| `mysql` | `mysql:8.0` | `3307:3306` | 宿主机 3307 映射容器 3306，避免与本机 MySQL 冲突；数据保存在命名卷 `mysql_data` |
| `redis` | `redis:7-alpine` | `6380:6379` | 启动参数带 `--appendonly yes`（AOF 持久化）；数据保存在命名卷 `redis_data` |
| `api` | 由 `Dockerfile` 构建 | `8000:8000` | 应用容器；`./uploads` 以 bind mount 挂载到 `/app/uploads` |

- **启动顺序**：`api` 通过 `depends_on` 的 `condition: service_healthy` 等待 MySQL 与 Redis 健康检查通过后再启动。
- **健康检查**：MySQL 用 `mysqladmin ping`（`start_period` 30 秒），Redis 用 `redis-cli ping`。
- **重启策略**：三个服务均为 `restart: unless-stopped`。

### 2. 环境变量

Compose 额外需要以下变量，`.env_example` 已包含该配置段，填入真实值即可：

```env
MYSQL_ROOT_PASSWORD=
MYSQL_DATABASE=
MYSQL_USER=
MYSQL_PASSWORD=
```

`api` 服务先用 `env_file: .env` 载入全部配置，再用 `environment` 覆盖容器内连接地址：

- `DATABASE_URL` 覆盖为 `mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mysql:3306/${MYSQL_DATABASE}`——主机名使用 Compose 服务名 `mysql`，端口是容器内 3306，而不是宿主机的 3307。
- `REDIS_HOST=redis`、`REDIS_PORT=6379`、`REDIS_DB=0`，同样通过服务名访问。
- `environment` 的优先级高于 `env_file`，`.env` 中指向 `127.0.0.1` 的地址不会生效。
- `TEST_DATABASE_URL` 不会被覆盖；若要在容器内跑 pytest，需要另外指向可用的测试库。

### 3. 启动与停止

```bash
# 构建镜像并后台启动全部服务
docker compose up -d --build

# 查看状态与日志
docker compose ps
docker compose logs -f api

# 停止并删除容器（保留数据卷）
docker compose down

# 停止并删除容器与数据卷（⚠️ 会清空 MySQL / Redis 数据）
docker compose down -v
```

启动后访问 <http://127.0.0.1:8000/docs>。从宿主机直连服务时，MySQL 使用 `127.0.0.1:3307`，Redis 使用 `127.0.0.1:6380`。

> **提示**：容器名在 `compose.yaml` 中定义为 `fastapi-week3-mysql` / `fastapi-week3-redis` / `fastapi-week3-api`（前缀为 week3，与项目名 week2 不一致，属历史遗留，不影响运行）。

## API 文档

### 认证方式

1. 调用 `POST /auth/register` 注册用户（JSON 请求体）。
2. 调用 `POST /auth/login` 登录，注意使用**表单**数据（`application/x-www-form-urlencoded`，不是 JSON）。
3. 登录成功后拿到 `access_token`，后续请求在请求头中携带：

```text
Authorization: Bearer <access_token>
```

在 Swagger UI 中也可以点击右上角的 **Authorize**，填入用户名和密码，Swagger 会自动登录并保存 token，之后访问受保护接口会自动带上请求头。

### 接口列表

| Method | Endpoint | 功能 | 认证 |
| --- | --- | --- | --- |
| POST | `/auth/register` | 注册 | 否 |
| POST | `/auth/login` | 登录（表单） | 否 |
| GET | `/auth/me` | 当前用户 | 是 |
| POST | `/users/` | 创建用户 | 是 |
| GET | `/users/` | 用户列表（分页） | 是 |
| GET | `/users/{user_id}` | 用户详情（Cache-Aside 缓存） | 是 |
| PUT | `/users/{user_id}` | 修改用户 | 是 |
| DELETE | `/users/{user_id}` | 删除用户 | 是 |
| POST | `/files/` | 上传文件 | 否 |
| GET | `/external/github/{username}` | 外部 API：GitHub 用户信息 | 否 |
| POST | `/ai/chat` | AI 问答（DeepSeek） | 否 |
| POST | `/ai/summarize` | AI 文本总结（DeepSeek） | 否 |
| POST | `/ai/extract` | AI 信息提取（DeepSeek，可切换少样本） | 否 |
| POST | `/ai/chat/stream` | AI 流式问答（SSE） | 否 |
| POST | `/cache/test/{key}` | 写入缓存（TTL 60 秒） | 否 |
| GET | `/cache/test/{key}` | 读取缓存 | 否 |
| GET | `/cache/test/{key}/ttl` | 查看剩余 TTL | 否 |
| DELETE | `/cache/test/{key}` | 删除缓存 | 否 |
| GET | `/cache/demo` | Cache-Aside 演示 | 否 |
| GET | `/health/` | 健康检查 | 否 |
| GET | `/` | 根路径 | 否 |

> **说明**：`POST /users/` 与 `POST /auth/register` 功能重叠，且 `/users/` 需要登录；日常注册请使用 `/auth/register`。

### 请求示例

```bash
# 注册
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"koko","password":"secret123","age":20}'

# 登录：表单数据，返回 {"access_token":"...","token_type":"bearer"}
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=koko&password=secret123"

# 当前用户
curl http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer <access_token>"

# 用户列表（需要登录）
curl "http://127.0.0.1:8000/users/?page=1&size=10" \
  -H "Authorization: Bearer <access_token>"

# 用户详情：首次 X-Cache: MISS，60 秒内再次请求 X-Cache: HIT
curl -i http://127.0.0.1:8000/users/1 \
  -H "Authorization: Bearer <access_token>"

# 上传文件（只允许 .txt / .md / .pdf，最大 5MB）
curl -X POST http://127.0.0.1:8000/files/ \
  -F "file=@README.md"

# 外部 GitHub API
curl http://127.0.0.1:8000/external/github/torvalds

# AI 问答：需要 .env 中配置 DEEPSEEK_API_KEY
curl -X POST http://127.0.0.1:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"用一句话解释什么是 FastAPI"}'

# 流式问答：-N 关闭 curl 缓冲，逐条打印 SSE 事件
curl -N -X POST http://127.0.0.1:8000/ai/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"用一句话解释什么是 FastAPI"}'

# 文本总结：按「一句话概括 / 主要内容 / 关键数据」输出
curl -X POST http://127.0.0.1:8000/ai/summarize \
  -H "Content-Type: application/json" \
  -d '{"text":"（粘贴一段需要总结的文本）"}'

# 信息提取：use_few_shot 可选，默认 false
curl -X POST http://127.0.0.1:8000/ai/extract \
  -H "Content-Type: application/json" \
  -d '{"text":"协会将于11月20日在教学楼101举办算法分享会，面向全校学生，报名截止11月18日。","use_few_shot":true}'

# 写入缓存：value 是查询参数，60 秒后过期
curl -X POST "http://127.0.0.1:8000/cache/test/name?value=koko"

# 读取、查看 TTL、删除
curl http://127.0.0.1:8000/cache/test/name
curl http://127.0.0.1:8000/cache/test/name/ttl
curl -X DELETE http://127.0.0.1:8000/cache/test/name

# 缓存旁路演示：首次请求慢，60 秒内再次请求命中缓存
curl http://127.0.0.1:8000/cache/demo
```

### 常见状态码

| 状态码 | 场景 |
| --- | --- |
| 201 | 创建成功（注册、创建用户、上传文件） |
| 204 | 删除成功 |
| 400 | 用户名已存在、文件格式不支持 |
| 401 | 未登录、Token 无效 / 过期、账号或密码错误 |
| 404 | 用户不存在、GitHub 用户不存在 |
| 413 | 上传文件超过 5MB |
| 422 | 请求参数 / 请求体校验失败 |
| 500 | 访问 `/cache/*` 或 `GET /users/{user_id}` 时 Redis 未启动或连接失败 |
| 502 | 外部 API 请求失败；大模型认证失败、连接失败或返回错误状态码 |
| 503 | 未配置 `DEEPSEEK_API_KEY`、大模型返回空回答，或请求受限 / 账户额度不足 |
| 504 | 请求大模型超时 |

## 测试方式

在项目根目录执行：

```bash
pytest -v
```

只运行某个测试文件：

```bash
pytest tests/test_auth.py -v
```

### 测试前提

- `.env` 中的 `TEST_DATABASE_URL` 必须指向一个**独立的测试数据库**。
- `GITHUB_TOKEN` 也必须配置：`tests/conftest.py` 会导入 `app.main`，而 `app/api/external.py` 在导入时就要求该变量存在。
- Redis 必须已启动：`GET /users/{user_id}` 会先读缓存，`test_get_user_not_found` 依赖 Redis 连接。

### 测试机制

- `tests/conftest.py` 用 `TestClient(app)` 创建测试客户端，并通过 `app.dependency_overrides[get_db]` 把数据库依赖切换为测试库会话。
- `reset_database` 是 `autouse=True` 的 fixture，**每条测试执行前都会 `drop_all` + `create_all`**，保证测试之间互不影响。
- `auth_headers` fixture 会注册并登录测试用户，返回带 Token 的请求头，供需要认证的用例复用。

> **⚠️ 警告**：测试会反复删除并重建测试库中的表。务必确认 `TEST_DATABASE_URL` 指向的是专用测试库，绝不能和 `DATABASE_URL` 相同，否则会清空开发数据。

### 测试覆盖

| 文件 | 覆盖内容 |
| --- | --- |
| `tests/test_health.py` | 健康检查、请求体字段校验 |
| `tests/test_ai_prompts.py` | 提示词消息构造：角色顺序、消息条数、文本包裹与零样本 / 少样本分支（不调用真实模型） |
| `tests/test_auth.py` | 注册成功 / 重名、登录成功 / 密码错误、`/auth/me` 无 Token / 有 Token |
| `tests/test_users.py` | 未登录访问返回 401、登录后查询列表、查询不存在的用户返回 404（先读缓存未命中，再查库） |
| `tests/test_files.py` | 上传合法 `.txt` 返回 201、上传 `.exe` 返回 400 |

> **提示**：上传测试会在 `uploads/` 目录留下测试文件；该目录已加入 `.gitignore`，不会提交到 Git。

> **提示**：`GET /users/{user_id}` 与 `/cache/*` 依赖真实 Redis；目前没有专门覆盖缓存命中 / 失效的 pytest 用例。

> **提示**：`tests/test_ai_prompts.py` 只测试消息构造，不会调用真实模型；`/ai/*` 接口本身（包括 `/ai/chat/stream` 流式接口）未编写自动化测试，现有 pytest 用例不依赖 `DEEPSEEK_API_KEY`（应用启动不要求该变量）。

> **提示**：`reset_database` 只重建测试数据库，**不会清理 Redis**。若用例涉及已缓存的用户，需手动删除对应 key，否则可能读到上一条用例留下的数据。

## 开发日志

### Day 1：FastAPI 基础（路由、参数与请求体）

- 创建 `FastAPI` 应用实例，理解 `app = FastAPI()` 与装饰器路由（`@app.get` / `@app.post`）。
- 路径参数：`/users/{user_id}` 配合类型注解 `user_id: int`，自动完成参数解析与类型转换。
- 查询参数：`/search?keyword=&page=&size=`，带默认值的参数（`page: int = 1`）变为可选。
- 请求体：使用 Pydantic `BaseModel` 定义 `UserCreate`（name / age），POST 提交 JSON 自动校验并解析。
- 通过 `uvicorn` 启动服务，使用内置交互式文档（`/docs`、`/redoc`）调试接口。

### Day 2：内存 CRUD（分页、响应模型与异常处理）

- 用模块级列表 `users` 配合自增变量 `next_id` 作为存储，数据只存在内存中，服务重启即清空。
- 按用途拆分 Pydantic 模型：`UserCreate`（创建入参校验）、`UserResponse`（统一响应结构）、`UserUpdate`（更新入参）。
- 用 `Field` 做字段级约束：`name` 限制 `min_length=1 / max_length=50`，`age` 限制 `gt=0 / lt=150`，非法值由 FastAPI 自动返回 422。
- 分页查询：`/users?page=&size=` 使用 `Query(default=1, ge=1, le=100)`，通过列表切片返回当页数据。
- 路径参数校验：`/users/{user_id}` 使用 `Path(gt=0)`，要求 ID 为正整数。
- 每个接口用 `response_model` 声明响应结构，创建接口设置 `status_code=201`。
- 异常处理：查找、更新、删除找不到用户时抛出 `HTTPException(status_code=404)`；创建时用户名重复返回 400。

### Day 3：项目分层重构（APIRouter、配置管理与中间件）

- **目录重构**：把 Day 1 / Day 2 的练习代码从主应用中剥离，主应用迁至 `app/`，按职责分层——`api/`（路由）、`schemas/`（数据模型）、`services/`（业务逻辑）、`core/`（配置与中间件）。
- **APIRouter 拆分路由**：`app/api/users.py` 定义 `APIRouter(prefix="/users", tags=["Users"])`，`app/main.py` 通过 `app.include_router()` 注册。
- **分层职责划分**：路由层只负责 HTTP 相关的事（参数校验、抛 `HTTPException`），业务逻辑下沉到 `app/services/user_service.py`；service 层用 `None` / `False` 表达“未找到”，由路由层决定返回什么错误码。
- **配置管理**：`app/core/config.py` 用 `pydantic-settings` 的 `BaseSettings` 定义配置类，通过 `SettingsConfigDict(env_file=".env")` 自动读取 `.env`。
- **中间件**：`app/core/middleware.py` 实现请求耗时统计，并在 `main.py` 中通过 `app.middleware("http")` 注册（Day 6 起主应用改用 `log_request_time`）。
- **健康检查**：新增 `app/api/health.py`，提供 `/health/` 接口返回 `{"status": "ok"}`。
- **应用元信息**：`FastAPI(title=setting.app_name, version="0.1.0")`，标题从配置读取。
- **依赖注入练习**：用 `Depends(common_params)` 把公共查询参数抽成可复用的依赖函数。
- **中间件练习**：单独练习了中间件的写法。
- **修正 Day 2 遗留问题**：删除接口的路径随 `prefix="/users"` 统一为 `/users/{user_id}`。

### Day 4：数据库接入（SQLAlchemy + MySQL）

- **数据库连接层**：`app/db/base.py` 用 SQLAlchemy 2.0 的 `DeclarativeBase` 定义声明基类 `Base`；`app/db/session.py` 用 `create_engine(setting.database_url)` 创建引擎，再通过 `sessionmaker` 得到会话工厂 `SessionLocal`。
- **会话依赖注入**：`get_db()` 是生成器函数，`yield` 出数据库会话、在 `finally` 中 `db.close()`；路由函数用 `db: Session = Depends(get_db)` 声明。
- **ORM 模型**：`app/models/user.py` 用 `Mapped[...]` + `mapped_column()` 定义 `User`，映射到 `users` 表——`id`（主键、自增）、`name`（`String(50)`、唯一、非空）、`age`（非空）。
- **自动建表**：`app/main.py` 中导入模型后执行 `Base.metadata.create_all(bind=engine)`，启动时自动创建缺失的表。
- **服务层改造**：`user_service.py` 由内存列表改为数据库操作——分页用 `offset/limit`，查单个用 `filter(...).first()`，创建用 `db.add()` + `commit()` + `refresh()`，删除用 `db.delete()` + `commit()`。
- **重名校验**：新增 `find_user_by_name()` 在创建前查重，同时 `name` 字段带 `unique=True` 作为数据库层兜底。
- **响应模型适配**：`UserResponse` 增加 `model_config = ConfigDict(from_attributes=True)`，Pydantic 才能直接从 ORM 对象读取属性。

### Day 5：用户认证（密码哈希 + JWT）

- **密码哈希**：`app/core/security.py` 用 `pwdlib` 的 `PasswordHash.recommended()`（底层为 Argon2）实现 `hash_password()` / `verify_password()`，数据库只保存哈希值。
- **JWT 签发**：`create_access_token(user_id)` 用 `PyJWT` 生成 token，payload 包含 `sub`（用户 ID）和 `exp`（UTC 过期时间）；有效期读 `ACCESS_TOKEN_EXPIRE_MINUTES`，签名密钥读 `SECRET_KEY`。
- **JWT 校验**：`decode_access_token(token)` 验签并解析 payload，捕获 `jwt.InvalidTokenError` 后统一返回 `None`。
- **数据模型调整**：`User` 增加 `password_hash` 列；`UserCreate` 增加 `password` 字段；`UserResponse` 不含密码相关字段。
- **注册**：`auth_service.register_user()` 先查重，再哈希密码后写库；`POST /auth/register` 成功返回 201，用户名已存在返回 400。
- **登录**：`POST /auth/login` 使用 `OAuth2PasswordRequestForm` 接收**表单**数据，成功返回 `{"access_token": ..., "token_type": "bearer"}`，账号或密码错误返回 401。
- **当前用户依赖**：`app/core/dependencies.py` 定义 `OAuth2PasswordBearer(tokenUrl="/auth/login")` 与 `get_current_user()`——从 `Authorization: Bearer <token>` 取出 token，解码后查用户；无效 token 或用户不存在都返回 401。
- **受保护接口**：`GET /auth/me` 通过 `Depends(get_current_user)` 返回当前登录用户。
- **复用已有逻辑**：`auth_service` 复用 `user_service.find_user_by_name()`，`get_current_user` 复用 `user_service.find_user()`。
- **待办**：`app/schemas/auth.py` 中的 `LoginRequest` 目前未被使用（登录实际使用表单）。

### Day 6：文件上传、外部 API 调用与 CORS

- **文件上传接口**：`POST /files/` 用 `UploadFile = File(...)` 接收 multipart 表单文件，成功返回 201。
- **上传目录**：`UPLOAD_DIR = Path("uploads")`，模块导入时自动创建；`uploads/` 已加入 `.gitignore`。
- **扩展名白名单**：只允许 `.txt`、`.md`、`.pdf`，其余格式返回 400。
- **大小限制**：`MAX_FILE_SIZE = 5 * 1024 * 1024`，按 1MB 分块读取并累计大小，超过 5MB 返回 413，并删除已写入的不完整文件。
- **存储文件名**：使用 `uuid4().hex` + 原扩展名，避免路径穿越和同名覆盖；响应返回 `filename`、`stored_as`、`size_bytes`。
- **资源释放**：成功、格式不支持、文件过大三种情况都会 `await file.close()`。
- **外部 API 调用**：`GET /external/github/{username}` 用 `httpx.AsyncClient(timeout=10.0)` 异步请求 GitHub 的 `/users/{username}` 接口。
- **请求头**：GitHub API 要求必须带 `User-Agent`；同时通过 `Authorization: token <GITHUB_TOKEN>` 认证，提高速率限制。
- **错误映射**：网络异常 / 连接失败返回 502，GitHub 返回 404 时映射为 404，其他非 2xx 返回 502；响应只挑选 `login`、`public_repos`、`followers`、`html_url` 四个字段。
- **配置读取**：`external.py` 在模块导入时 `load_dotenv()` 后读取 `os.getenv("GITHUB_TOKEN")`，缺失则直接 `raise ValueError`，应用启动即失败。
- **CORS**：`main.py` 通过 `CORSMiddleware` 允许 `http://localhost:5173` 与 `http://127.0.0.1:5173`（Vite 开发服务器默认端口）跨域访问。
- **请求日志中间件升级**：`log_request_time` 使用 `time.perf_counter()` 计时，在响应头写入 `X-Process-Time`（单位 ms），并打印 `方法 路径 状态码 耗时`，形如 `GET /users/ 200 3.12ms`。

### Day 7：pytest 自动化测试

- **测试基础设施**：`tests/conftest.py` 用 `TestClient(app)` 创建客户端，并用 `app.dependency_overrides[get_db]` 把数据库切换为测试库。
- **独立测试库**：`Settings` 新增 `test_database_url`，`.env_example` 同步新增 `TEST_DATABASE_URL`。
- **数据隔离**：`reset_database` fixture 标记 `autouse=True`，每条测试前执行 `drop_all` + `create_all`。
- **认证 fixture**：`auth_headers` 注册并登录测试用户，返回带 Token 的请求头。
- **接口保护**：`/users` 路由整体挂载 `dependencies=[Depends(get_current_user)]`，测试中未登录访问返回 401。
- **测试用例**：覆盖健康检查、注册 / 重名、登录成功 / 密码错误、`/auth/me` 有无 Token、用户列表、用户不存在、合法 / 非法文件上传。

### Day 8：Redis 缓存

- **配置**：`Settings` 新增 `redis_host` / `redis_port` / `redis_db`，`.env_example` 同步新增三个变量。
- **异步客户端**：`app/cache/client.py` 用 `redis.asyncio.Redis` 创建全局客户端，开启 `decode_responses=True`，读取结果直接为字符串。
- **缓存读写接口**：`app/api/cache.py` 提供 `/cache/test/{key}` 的写入（`ex=60`）、读取、删除，以及 `/cache/test/{key}/ttl` 查询剩余过期时间。
- **写入参数**：`POST /cache/test/{key}` 的 `value` 定义为普通函数参数，实际作为查询参数传入，而不是 JSON 请求体。
- **缓存未命中**：读取接口在 key 不存在时返回 `{"hit": false, "value": null}`。
- **TTL 语义**：直接透传 Redis `TTL` 的结果——正数为剩余秒数，`-1` 表示永不过期，`-2` 表示 key 不存在。
- **缓存旁路演示**：`GET /cache/demo` 先查缓存，未命中时用 `asyncio.sleep(2)` 模拟慢查询，写入 60 秒缓存后再返回，响应中的 `source` 字段区分 `redis` 与 `slow source`。
- **独立练习脚本**：`examples/redis_demo.py` 用同步客户端演示 `set` / `get` / `ex` / `ttl` 的基本用法，不参与应用运行。

### Day 9：用户详情缓存（Cache-Aside 落地）

- **缓存模块**：新增 `app/cache/user_cache.py`，封装 `set_user_cache()` / `get_user_cache()` / `delete_user_cache()`，key 由 `user_cache_key(user_id)` 统一生成，格式为 `user:{user_id}`。
- **序列化**：缓存值是 JSON 字符串（`json.dumps` / `json.loads`），只保存 `id`、`name`、`age` 三个字段。
- **TTL 配置**：`Settings` 新增 `user_cache_ttl`，默认 60 秒；`.env_example` 暂未同步该变量。
- **读缓存**：`GET /users/{user_id}` 改为 `async`，先查 Redis——命中直接返回并设置 `X-Cache: HIT`；未命中查 MySQL、写入缓存后返回，设置 `X-Cache: MISS`。
- **未命中语义**：`get_user_cache()` 在 key 不存在时返回 `None`，由路由层继续查库并判断 404。
- **缓存失效**：`PUT` 与 `DELETE /users/{user_id}` 也改为 `async`，数据库操作成功后调用 `delete_user_cache()`，避免读到旧数据。
- **副作用**：用户详情接口从此依赖 Redis；本地调试与 pytest 都需要先启动 Redis。

### Day 10：Docker 容器化

- **Dockerfile**：基于 `python:3.13-slim`，设置 `PYTHONDONTWRITEBYTECODE=1` / `PYTHONUNBUFFERED=1`，`WORKDIR /app`。
- **构建缓存优化**：先 `COPY requirements.txt` 并 `pip install`，再 `COPY . .`，依赖不变时重新构建会命中缓存。
- **启动命令**：`CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`，容器内监听 `0.0.0.0` 才能被端口映射访问；未带 `--reload`，代码改动需重新构建镜像。
- **`.dockerignore`**：排除 `.venv/`、`__pycache__/`、`*.py[cod]`、`.git/`、`.env`、`uploads/`、`.pytest_cache/`，减小构建上下文体积并避免密钥进入镜像。
- **运行方式**：`docker run --env-file .env` 在运行时注入配置，因为 `.env` 不在镜像内；连接宿主机上的 MySQL / Redis 时需使用 `host.docker.internal`。

### Day 11：Docker Compose 编排

- **编排文件**：新增 `compose.yaml`，定义 `mysql`、`redis`、`api` 三个服务，一条 `docker compose up -d --build` 拉起完整环境。
- **MySQL 服务**：`mysql:8.0`，宿主机端口 3307 映射容器 3306，避开本机已占用的 3306；初始化变量来自 `.env` 中的 `MYSQL_ROOT_PASSWORD` / `MYSQL_DATABASE` / `MYSQL_USER` / `MYSQL_PASSWORD`；数据持久化到命名卷 `mysql_data`。
- **Redis 服务**：`redis:7-alpine`，开启 AOF（`--appendonly yes`），宿主机端口 6380 映射容器 6379；数据持久化到命名卷 `redis_data`。
- **健康检查**：MySQL 用 `mysqladmin ping`、Redis 用 `redis-cli ping`；`api` 通过 `depends_on` 的 `condition: service_healthy` 等两者就绪后再启动，避免启动瞬间连不上依赖。
- **容器内连接配置**：`api` 服务用 `environment` 把 `DATABASE_URL` 覆盖为指向服务名 `mysql:3306` 的地址、`REDIS_HOST` 覆盖为 `redis`；`environment` 优先级高于 `env_file`，`.env` 里写给宿主机用的 `127.0.0.1` 不会生效。
- **文件持久化**：`./uploads` 以 bind mount 挂载到容器 `/app/uploads`，容器删除重建后上传文件仍保留。
- **重启策略与数据卷**：三个服务均为 `restart: unless-stopped`；`docker compose down` 保留命名卷，`docker compose down -v` 才会删除 MySQL / Redis 数据。

### Day 12：接入大模型（DeepSeek）

- **依赖**：新增 `openai` SDK，通过其 OpenAI 兼容接口访问 DeepSeek，依赖清单已重新导出为 UTF-8。
- **配置**：`Settings` 新增 `deepseek_api_key` / `llm_base_url` / `llm_model` / `llm_timeout`；`.env_example` 同步新增四个变量，并补上此前遗漏的 `USER_CACHE_TTL`。
- **客户端**：`app/ai/client.py` 用 `lru_cache(maxsize=1)` 复用 `AsyncOpenAI` 客户端，`timeout` 读取配置、`max_retries=2`；API Key 为空时在首次调用抛出 `RuntimeError`，不影响应用启动。
- **调用封装**：`generate_answer()` 调用 `chat.completions.create()`，校验 `choices` 非空且回答内容不为空，返回去除首尾空白的文本。
- **业务层**：`app/services/ai_service.py` 的 `chat_with_ai()` 在用户问题前拼接中文系统提示词。
- **接口**：`POST /ai/chat`，`ChatRequest` 限制 `message` 1–4000 字符并去除首尾空白；`ChatResponse` 返回 `answer` 与 `model`。
- **错误映射**：未配置 Key / 空回答 → 503；认证失败、连接失败、服务端错误 → 502；超时 → 504。
- **练习脚本**：`app/ai/llm_test.py` 用同步 `OpenAI` 客户端在终端交互调用 DeepSeek，不参与应用运行。

### Day 13：Prompt 工程（提示词模板、少样本与文本任务接口）

- **提示词集中管理**：新增 `app/ai/prompts.py`，把系统提示词从业务代码中剥离，统一按「角色 / 任务 / 约束 / 输出格式」组织。
- **消息构造**：`build_chat_messages()` / `build_summary_messages()` / `build_extract_messages()` 返回 OpenAI `messages` 格式的消息列表，system 提示词与用户输入分离。
- **文本总结**：`SUMMARY_SYSTEM_PROMPT` 要求按「一句话概括 / 主要内容（3～5 个要点）/ 关键数据」格式输出，只依据原文、不添加原文没有的信息。
- **信息提取**：`EXTRACT_SYSTEM_PROMPT` 定义七个提取字段（事项名称、时间、地点、组织方、面向对象、截止时间、联系方式），缺失字段填「未提及」；`use_few_shot=True` 时插入两组示例问答。
- **提示词注入防护**：总结与提取用 `<待处理文本>` 标签包裹用户输入；提取提示词额外声明标签内的指令不生效。
- **客户端扩展**：`generate_answer()` 改为接收 `messages` 并支持可选 `temperature`（校验 0–2）；设置 temperature 时通过 `extra_body` 关闭 DeepSeek 的 thinking 模式。
- **业务层**：`ai_service.py` 新增 `summarize_text()` 与 `extract_key_info()`，两者使用 `temperature=0.2`；`chat_with_ai()` 改用 `build_chat_messages()`。
- **接口**：新增 `POST /ai/summarize`（`TextRequest`，1–8000 字符）与 `POST /ai/extract`（`ExtractRequest` 继承 `TextRequest`，增加 `use_few_shot`）。
- **错误映射**：抽取统一异常处理 `_run_ai_task()`，新增 `RateLimitError` → 503（请求受限或账户额度不足）。
- **实验脚本**：`app/ai/prompt_experiment.py` 用 temperature 0.2 / 0.7 / 1.2 调用同一问题并对比输出，不参与应用运行。
- **测试**：`tests/test_ai_prompts.py` 覆盖三种消息构造函数以及零样本 / 少样本分支，只校验消息结构，不调用真实模型。

### Day 14：SSE 流式输出

- **流式客户端**：`app/ai/client.py` 新增 `stream_answer()`，以 `stream=True` 调用 `chat.completions.create()`，逐段 `yield` 增量文本，跳过空 chunk，关闭 thinking 模式，并在 `finally` 中关闭流。
- **业务层**：`app/services/ai_service.py` 新增 `stream_chat_with_ai()`，复用 `build_chat_messages()` 后异步迭代 `stream_answer()`。
- **接口**：新增 `POST /ai/chat/stream`，请求体复用 `ChatRequest`，通过 FastAPI 内置 `EventSourceResponse` 返回 `text/event-stream`。
- **事件协议**：增量内容为 `delta` 事件，data 为 `{"type": "delta", "content": "..."}`；正常结束发送 `done`；异常发送 `error`。
- **断连处理**：每段输出前检查 `request.is_disconnected()`，客户端断开后停止生成，且不发送 `done`。
- **错误处理**：流式响应开始后无法修改 HTTP 状态码，限流 / 超时 / 连接失败 / 服务端错误 / 未配置 Key 统一转换为 `error` 事件；请求体校验仍在推送前返回 422。

## 更新依赖

新增第三方库后，重新导出依赖清单：

```bash
pip freeze > requirements.txt
```

> **提示**：Windows PowerShell 的重定向默认生成 UTF-16 编码的文件，Git 会把它当成二进制文件，diff 不可读，部分工具也可能读取异常。可改用 `pip freeze | Out-File -Encoding utf8 requirements.txt`。当前仓库中的 `requirements.txt` 已是 UTF-8，重新导出时请保持该编码。
