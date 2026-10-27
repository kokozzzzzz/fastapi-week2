# FastAPI Week 2

一个用于系统学习 FastAPI 的后端练习项目。项目从基础路由开始，逐步覆盖 Pydantic 数据校验、分层架构、MySQL 持久化、JWT 用户认证、文件上传、外部 API 调用、pytest 接口测试与 Redis 缓存，最终形成一个结构清晰、可运行、可测试的 FastAPI 应用。

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
| 服务器 | Uvicorn |
| 测试 | pytest、FastAPI TestClient |

## 功能

- **用户管理**：用户的增删改查与分页查询，数据持久化到 MySQL；用户名唯一，字段由 Pydantic 校验。
- **用户认证**：注册、登录、获取当前用户；密码使用 Argon2 哈希后入库，登录返回 JWT，受保护接口通过 `Authorization: Bearer <token>` 访问。
- **接口保护**：`/users` 路由整体挂载 `get_current_user` 依赖，未携带有效 token 的请求统一返回 401。
- **文件上传**：仅允许 `.txt` / `.md` / `.pdf`，单文件最大 5MB；文件以 UUID 重命名保存至 `uploads/`，原始文件名随响应返回。
- **外部 API**：通过 `httpx` 异步调用 GitHub 用户接口，返回精简后的公开信息，并映射 404 / 502 错误。
- **Redis 缓存**：基于 `redis.asyncio` 的异步客户端，支持缓存写入（60 秒 TTL）、读取、删除与 TTL 查询；`/cache/demo` 演示 Cache-Aside 模式。
- **用户详情缓存**：`GET /users/{user_id}` 采用 Cache-Aside，key 为 `user:{user_id}`，TTL 由 `USER_CACHE_TTL` 控制（默认 60 秒）；响应头 `X-Cache` 标记 `HIT` / `MISS`，更新或删除用户时自动使缓存失效。
- **基础设施**：健康检查、请求耗时中间件（响应头 `X-Process-Time`）、CORS（允许 Vite 开发服务器跨域）。
- **自动化测试**：pytest + TestClient，使用独立测试数据库，覆盖认证、用户、文件上传与健康检查。

## 目录结构

```text
FastAPI-week2/
├── app/                          # 主应用
│   ├── main.py                   # 应用入口：创建 FastAPI 实例、注册中间件 / CORS / 路由、自动建表
│   ├── api/                      # 路由层：只处理 HTTP 请求与响应
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
│   │   ├── auth.py               # 登录 / Token 响应模型
│   │   └── user.py               # UserCreate / UserUpdate / UserResponse
│   └── services/                 # 业务逻辑层
│       ├── auth_service.py       # 注册与登录校验
│       └── user_service.py       # 用户增删改查
│
├── tests/                        # pytest 自动化测试
│   ├── conftest.py               # 测试数据库、TestClient、auth_headers fixture
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
| `USER_CACHE_TTL` | 否 | 用户详情缓存过期时间（秒），默认 `60`。`.env_example` 暂未列出该变量，需要修改默认值时手动添加到 `.env` |

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

> **提示**：`/users/`、`/files/`、`/health/` 带结尾斜杠，请求不带斜杠的路径会收到 307 重定向；`/auth/...`、`/external/...`、`/cache/...` 不带结尾斜杠。

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
| 502 | 外部 API 请求失败 |

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
| `tests/test_auth.py` | 注册成功 / 重名、登录成功 / 密码错误、`/auth/me` 无 Token / 有 Token |
| `tests/test_users.py` | 未登录访问返回 401、登录后查询列表、查询不存在的用户返回 404（先读缓存未命中，再查库） |
| `tests/test_files.py` | 上传合法 `.txt` 返回 201、上传 `.exe` 返回 400 |

> **提示**：上传测试会在 `uploads/` 目录留下测试文件；该目录已加入 `.gitignore`，不会提交到 Git。

> **提示**：`GET /users/{user_id}` 与 `/cache/*` 依赖真实 Redis；目前没有专门覆盖缓存命中 / 失效的 pytest 用例。

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

## 更新依赖

新增第三方库后，重新导出依赖清单：

```bash
pip freeze > requirements.txt
```

> **提示**：Windows PowerShell 的重定向默认生成 UTF-16 编码的文件，Git 会把它当成二进制文件，diff 不可读，部分工具也可能读取异常。可改用 `pip freeze | Out-File -Encoding utf8 requirements.txt`。当前仓库中的 `requirements.txt` 是 UTF-16 LE（带 BOM），建议重新导出为 UTF-8。
