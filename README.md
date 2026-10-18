# FastAPI 项目练习（Week 2）

这是一个 FastAPI 学习练习项目，承接 Week 1 的 Python 基础练习（见 `python-test`），按“每日一个独立模块”的方式组织。每日的练习文件存放在 `tests/` 下；从 Day 3 起，在练习的基础上把代码重构为 `app/` 分层结构，作为后续开发的主应用。所有模块共享同一个虚拟环境。

## 项目内容

### Day 1：FastAPI 基础（路由、参数与请求体）
- 创建 `FastAPI` 应用实例，理解 `app = FastAPI()` 与装饰器路由（`@app.get` / `@app.post`）
- 路径参数：`/users/{user_id}` 配合类型注解 `user_id: int`，自动完成参数解析与类型转换
- 查询参数：`/search?keyword=&page=&size=`，带默认值的参数（`page: int = 1`）变为可选
- 请求体：使用 Pydantic `BaseModel` 定义 `UserCreate`（name / age），POST 提交 JSON 自动校验并解析
- 通过 `uvicorn` 启动服务，使用内置交互式文档（`/docs`、`/redoc`）调试接口
- `tests/day1_test.py` 中已用注释预留商品接口（`/products/{product_id}`、`/products?category=`、`ProductCreate` 的 `Field(gt=0)` 校验）作为后续练习

### Day 2：内存 CRUD（分页、响应模型与异常处理）
- 用模块级列表 `users` 配合自增变量 `next_id` 作为存储，数据只存在内存中，服务重启即清空；`find_user(user_id)` 抽出按 ID 查找的逻辑
- 按用途拆分 Pydantic 模型：`UserCreate`（创建入参校验）、`UserResponse`（统一响应结构）、`UserUpdate`（更新入参）
- 用 `Field` 做字段级约束：`name` 限制 `min_length=1 / max_length=50`，`age` 限制 `gt=0 / lt=150`，非法值由 FastAPI 自动返回 422
- 分页查询：`/users?page=&size=` 使用 `Query(default=1, ge=1, le=100, description="页码")`，通过列表切片 `users[start:end]` 返回当页数据
- 路径参数校验：`/users/{user_id}` 使用 `Path(gt=0)`，要求 ID 为正整数
- 每个接口用 `response_model` 声明响应结构，创建接口设置 `status_code=201`
- 异常处理：查找、更新、删除找不到用户时抛出 `HTTPException(status_code=404, detail="用户未找到")`；创建时用户名重复返回 400
- 练习状态码语义：创建成功 201、删除成功 204、资源不存在 404、用户名已存在 400

### Day 3：项目分层重构（APIRouter、配置管理与中间件）
- **目录重构**：把 Day 1 / Day 2 的练习文件移入 `tests/`，主应用迁至 `app/`，按职责分层——`api/`（路由）、`schemas/`（数据模型）、`services/`（业务逻辑）、`core/`（配置与中间件）
- **APIRouter 拆分路由**：`app/api/users.py` 定义 `APIRouter(prefix="/users", tags=["Users"])`，`app/main.py` 通过 `app.include_router()` 注册，入口文件不再堆砌所有接口
- **分层职责划分**：路由层只负责 HTTP 相关的事（参数校验、抛 `HTTPException`），业务逻辑下沉到 `app/services/user_service.py`；service 层用 `None` / `False` 表达“未找到”，由路由层决定返回什么错误码，不再由 service 层直接抛 HTTP 异常
- **配置管理**：`app/core/config.py` 用 `pydantic-settings` 的 `BaseSettings` 定义配置类，通过 `SettingsConfigDict(env_file=".env", extra="ignore")` 自动读取 `.env`，应用名等信息不再硬编码
- **中间件**：`app/core/middleware.py` 实现 `add_process_time`，用 `time.time()` 记录每个请求的耗时并打印到控制台，在 `main.py` 中通过 `app.middleware("http")` 注册
- **健康检查**：新增 `app/api/health.py`，提供 `/health/` 接口返回 `{"status": "ok"}`
- **应用元信息**：`FastAPI(title=setting.app_name, version="0.1.0")`，标题从配置读取
- **依赖注入练习**：`tests/day3_depends_demo.py` 用 `Depends(common_params)` 把公共查询参数抽成可复用的依赖函数
- **中间件练习**：`tests/day3_time_demo.py` 单独练习中间件的写法
- **修正 Day 2 遗留问题**：删除接口的路径随 `prefix="/users"` 统一为 `/users/{user_id}`，不再是与其余接口不一致的 `/user/{user_id}`
- **新增依赖**：`pydantic-settings`（配置管理用，`python-dotenv` 作为其依赖一并安装）

### Day 4：数据库接入（SQLAlchemy + MySQL）
- **新增数据库连接层**：`app/db/base.py` 用 SQLAlchemy 2.0 的 `DeclarativeBase` 定义声明基类 `Base`；`app/db/session.py` 用 `create_engine(setting.database_url)` 创建引擎，再通过 `sessionmaker(bind=engine, autoflush=False, autocommit=False)` 得到会话工厂 `SessionLocal`
- **会话依赖注入**：`get_db()` 是生成器函数，`yield` 出数据库会话、在 `finally` 中 `db.close()`；路由函数用 `db: Session = Depends(get_db)` 声明，FastAPI 负责在请求结束时关闭会话
- **ORM 模型**：`app/models/user.py` 用 `Mapped[...]` + `mapped_column()` 的注解写法定义 `User`，映射到 `users` 表——`id`（主键、自增）、`name`（`String(50)`、唯一、非空）、`age`（非空）
- **自动建表**：`app/main.py` 中导入模型后执行 `Base.metadata.create_all(bind=engine)`，启动时自动创建缺失的表（只建新表，不会修改已存在的表结构）
- **服务层改造**：`app/services/user_service.py` 由内存列表改为数据库操作，每个函数第一个参数是 `db: Session`——分页用 `db.query(User).offset(start).limit(size).all()`，查单个用 `filter(User.id == user_id).first()`，创建用 `db.add()` + `db.commit()` + `db.refresh()`（刷新后才能拿到自增 id），删除用 `db.delete()` + `db.commit()`
- **重名校验**：新增 `find_user_by_name()` 在创建前查重，同时 `name` 字段带 `unique=True` 作为数据库层的兜底约束
- **响应模型适配**：`UserResponse` 增加 `model_config = ConfigDict(from_attributes=True)`，Pydantic 才能直接从 ORM 对象（而不是 dict）读取属性
- **配置新增**：`Settings` 增加 `database_url`、`github_token` 字段，`DATABASE_URL` 从 `.env` 读取，连接串格式为 `mysql+pymysql://用户名:密码@主机:端口/数据库名`
- **补齐路径校验**：`GET /users/{user_id}` 的 `user_id` 补上 `Path(gt=0)`，与更新、删除接口保持一致
- **新增依赖**：`SQLAlchemy`（ORM）、`PyMySQL`（MySQL 驱动）

### Day 5：用户认证（密码哈希 + JWT）
- **密码哈希**：`app/core/security.py` 用 `pwdlib` 的 `PasswordHash.recommended()`（底层为 Argon2）实现 `hash_password()` / `verify_password()`，数据库只保存哈希值，注册和登录全程不接触明文密码
- **JWT 签发**：`create_access_token(user_id)` 用 `PyJWT` 生成 token，payload 包含 `sub`（用户 ID，按 JWT 规范转成字符串）和 `exp`（UTC 过期时间）；有效期读 `ACCESS_TOKEN_EXPIRE_MINUTES`（默认 30 分钟），签名密钥读 `SECRET_KEY`，算法读 `ALGORITHM`（默认 `HS256`）
- **JWT 校验**：`decode_access_token(token)` 验签并解析 payload，捕获 `jwt.InvalidTokenError`（伪造、被篡改或已过期）后统一返回 `None`，校验通过则把 `sub` 转回 `int` 用户 ID
- **数据模型调整**：`User` 增加 `password_hash` 列（`String(255)`、非空）；`UserCreate` 增加 `password` 字段（`Field(min_length=6, max_length=128)`）；`UserResponse` 不含密码相关字段，避免泄露
- **注册**：`app/services/auth_service.py` 的 `register_user()` 先调用 `find_user_by_name()` 查重，再用 `hash_password()` 哈希后写库；`POST /auth/register` 成功返回 201，用户名已存在返回 400
- **登录**：`authenticate_user()` 按用户名查用户并 `verify_password()` 校验；`POST /auth/login` 使用 `OAuth2PasswordRequestForm` 接收**表单**数据（`username` / `password`，不是 JSON），成功返回 `{"access_token": ..., "token_type": "bearer"}`，账号或密码错误返回 401
- **当前用户依赖**：`app/core/dependencies.py` 定义 `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")` 与 `get_current_user()`——从请求头 `Authorization: Bearer <token>` 取出 token，解码后查用户；token 无效 / 过期或用户不存在都返回 401，并带 `WWW-Authenticate: Bearer` 响应头
- **受保护接口**：`GET /auth/me` 通过 `Depends(get_current_user)` 返回当前登录用户的信息
- **复用已有逻辑**：`auth_service` 复用 `user_service.find_user_by_name()`，`get_current_user` 复用 `user_service.find_user()`，没有重复写查询
- **连带调整用户创建**：`user_service.create_user()` 也改为先哈希密码再入库，因此 `POST /users/` 的请求体现在同样必须带 `password`（与 `/auth/register` 功能有重叠）
- **待办**：`app/schemas/auth.py` 定义了 `LoginRequest`，但登录接口实际用的是表单 `OAuth2PasswordRequestForm`，该类目前未被使用
- **新增依赖**：`PyJWT`（签发 / 校验 JWT）、`pwdlib` + `argon2-cffi`（密码哈希）、`python-multipart`（解析登录表单）

## 项目结构

```text
FastAPI-week2/
├── .env                       # 本地私有配置，存放 Token / API Key（不提交至 Git）
├── .env_example               # 环境变量模板（可提交至 Git）
├── .gitattributes
├── .gitignore
├── requirements.txt
├── README.md
├── conftest.py                # 空文件，让 pytest 把项目根加入 sys.path
├── data/                      # 练习数据目录（暂为空）
├── output/                    # 数据保存目录（暂为空）
│
├── app/                       # 主应用（Day 3 分层结构 + Day 4 数据层 + Day 5 认证）
│   ├── __init__.py
│   ├── main.py                # 应用入口：创建 FastAPI 实例、注册中间件与路由、自动建表
│   ├── api/                   # 路由层：只处理 HTTP 请求与响应
│   │   ├── __init__.py
│   │   ├── auth.py            # /auth 注册、登录、当前用户（Day 5 新增）
│   │   ├── health.py          # /health/ 健康检查
│   │   └── users.py           # /users 用户相关接口
│   ├── core/                  # 基础设施层
│   │   ├── __init__.py
│   │   ├── config.py          # 配置类，从 .env 读取 app_name / database_url / secret_key 等
│   │   ├── dependencies.py    # OAuth2PasswordBearer + get_current_user 依赖（Day 5 新增）
│   │   ├── middleware.py      # 请求耗时中间件
│   │   └── security.py        # 密码哈希与 JWT 签发 / 校验（Day 5 新增）
│   ├── db/                    # 数据库连接层（Day 4 新增）
│   │   ├── base.py            # 声明基类 Base
│   │   └── session.py         # engine / SessionLocal / get_db 依赖
│   ├── models/                # ORM 模型层（Day 4 新增）
│   │   └── user.py            # User 模型（含 password_hash），映射 users 表
│   ├── schemas/               # 数据模型层
│   │   ├── __init__.py
│   │   ├── auth.py            # LoginRequest / TokenResponse（Day 5 新增）
│   │   └── user.py            # UserCreate（含 password）/ UserUpdate / UserResponse
│   └── services/              # 业务逻辑层
│       ├── __init__.py
│       ├── auth_service.py    # 注册与登录校验（Day 5 新增）
│       └── user_service.py    # 用户增删改查的具体实现（操作数据库）
│
└── tests/                     # 每日练习代码
    ├── day1_test.py           # Day1：基础路由 / 路径参数 / 查询参数 / 请求体
    ├── day2_test.py           # Day2：内存 CRUD / 分页 / 响应模型与异常处理
    ├── day3_depends_demo.py   # Day3：Depends 依赖注入练习（应用实例变量名为 router）
    └── day3_time_demo.py      # Day3：中间件练习
```

> **说明**：`app/db/` 与 `app/models/` 暂未放置 `__init__.py`，依赖 Python 的命名空间包机制导入，可以正常工作；若想与其余目录保持一致，补两个空文件即可。

## 环境
- Python 3.13.14
- 操作系统：Windows 11
- 数据库：MySQL（Day 4 起接入，Python 驱动为 `PyMySQL`）

## 安装步骤

1.克隆项目
```bash
git clone https://github.com/yourname/FastAPI-week2.git
cd FastAPI-week2
```

2.创建虚拟环境
```bash
python -m venv .venv
```

3.激活虚拟环境

Windows:
```bash
.venv\Scripts\activate
```

macOS / Linux:
```bash
source .venv/bin/activate
```

4.安装依赖

```bash
pip install -r requirements.txt
```

5.导出依赖
```bash
pip freeze > requirements.txt
```

> **提示**：Windows PowerShell 的重定向默认生成 UTF-16 编码的文件，可能导致其他环境读取异常（Git 也会把它当二进制文件处理，无法正常 diff）。可改用 `pip freeze | Out-File -Encoding utf8 requirements.txt`。
>
> 当前仓库中的 `requirements.txt` 即为 UTF-16 编码，属于待修正项。

## 配置说明

根目录的 `.env_example` 提供了环境变量模板，将其中内容复制为 `.env` 后填入真实值：

```bash
cp .env_example .env
```

```env
GITHUB_TOKEN=
APP_NAME=
DEBUG=
DATABASE_URL=
SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

- **Day 3 已使用**：`APP_NAME`、`DEBUG`，由 `app/core/config.py` 的 `Settings` 类读取，分别对应字段 `app_name`、`debug`（`pydantic-settings` 默认大小写不敏感，`.env` 里写大写、代码里用小写即可）。
- **Day 4 新增字段**：`DATABASE_URL`、`GITHUB_TOKEN`，对应 `database_url`、`github_token`。其中 `DATABASE_URL` 是 SQLAlchemy 连接串，格式为 `mysql+pymysql://用户名:密码@主机:端口/数据库名`，需要先在 MySQL 中建好这个数据库（表由应用启动时自动创建）；`github_token` 目前只是读进来，尚未使用。
- **Day 5 新增字段**：`SECRET_KEY`、`ALGORITHM`、`ACCESS_TOKEN_EXPIRE_MINUTES`，对应 `secret_key`、`algorithm`、`access_token_expire_minutes`。`SECRET_KEY` 是 JWT 的签名密钥，字段没有默认值，**必须填写**（缺失时启动会报错），建议用足够长的随机字符串；`ALGORITHM` 默认 `HS256`；`ACCESS_TOKEN_EXPIRE_MINUTES` 是 token 有效期（分钟），默认 30。
- 也可以继续用 `os.getenv("XXX")` 读取配置，两种方式并存。
- 确认 `.gitignore` 中包含 `.env`，防止密钥被提交至 Git；`.env_example` 只放变量名、不放真实值，可以提交。

> **⚠️ 安全提示**：Token 和 API Key 等同于密码，请勿直接写在代码中，也不要上传至 GitHub。

> **注意**：`SettingsConfigDict(env_file=".env")` 中的路径是相对路径，相对**当前工作目录**解析。因此启动服务时请在项目根目录执行下面的命令，否则 `.env` 会读取不到：多数字段会退回代码里的默认值，而 `secret_key` 没有默认值，Day 5 起会直接启动失败。

## 运行方式

**启动主应用（Day 3 分层结构 + Day 4 数据库 + Day 5 认证）：**

```bash
python -m uvicorn app.main:app --reload
```

> **运行前准备（Day 4 起）**：先在本地启动 MySQL 服务并创建好 `.env` 中 `DATABASE_URL` 指向的数据库（例如 `CREATE DATABASE fastapi_week2 DEFAULT CHARSET utf8mb4;`），然后按下面的命令启动应用——`users` 表会在启动时由 `Base.metadata.create_all()` 自动创建，不需要手写建表 SQL。

> **⚠️ Day 5 表结构变更**：`User` 新增了 `password_hash` 列（非空），但 `create_all()` 只创建缺失的表，**不会修改已存在的表**。如果数据库里已经有 Day 4 建的 `users` 表，需要手动处理，例如：
>
> ```sql
> ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT '';
> ```
>
> 已有用户没有密码，补上空默认值后这些账号无法登录（需要重新注册或更新密码）；也可以直接删表让应用重建，但会丢失已有数据。项目目前尚未接入 Alembic 迁移工具。

**启动 Day 1 / Day 2 的练习文件：**

```bash
python -m uvicorn tests.day1_test:app --reload
python -m uvicorn tests.day2_test:app --reload
```

**启动 Day 3 的练习文件：**

```bash
python -m uvicorn tests.day3_time_demo:app --reload

# 注意：该文件里的 FastAPI 实例变量名是 router，不是 app
python -m uvicorn tests.day3_depends_demo:router --reload
```

默认监听 `http://127.0.0.1:8000`，`--reload` 表示代码变更后自动重启。

**访问交互式文档：**

- Swagger UI：http://127.0.0.1:8000/docs
- ReDoc：http://127.0.0.1:8000/redoc

**用 curl 测试接口（Day 1）：**

```bash
# 路径参数
curl http://127.0.0.1:8000/users/7

# 查询参数
curl "http://127.0.0.1:8000/search?keyword=book&page=2&size=5"

# 请求体
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"koko","age":23}'
```

### Day 1 接口一览

| 方法 | 路径 | 参数 | 说明 |
| --- | --- | --- | --- |
| GET | `/users/{user_id}` | 路径参数 `user_id: int` | 返回欢迎信息与用户 ID |
| GET | `/search` | 查询参数 `keyword`（必填）、`page`（默认 1）、`size`（默认 10） | 演示带默认值的查询参数 |
| POST | `/users` | 请求体 `UserCreate`：`name`、`age` | 演示 Pydantic 模型接收 JSON 请求体 |

**用 curl 测试接口（Day 2）：**

```bash
# 创建用户（重名返回 400）
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"koko","age":23}'

# 分页查询
curl "http://127.0.0.1:8000/users?page=1&size=10"

# 查询单个（不存在返回 404）
curl http://127.0.0.1:8000/users/1

# 更新
curl -X PUT http://127.0.0.1:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"koko2","age":24}'

# 删除（成功返回 204）
curl -X DELETE http://127.0.0.1:8000/users/1
```

### Day 2 接口一览

| 方法 | 路径 | 参数 | 说明 |
| --- | --- | --- | --- |
| POST | `/users` | 请求体 `UserCreate`：`name`（1～50 字符）、`age`（0～150） | 创建用户，成功返回 201，用户名已存在返回 400 |
| GET | `/users` | 查询参数 `page`（默认 1）、`size`（默认 10），取值 1～100 | 分页返回用户列表 |
| GET | `/users/{user_id}` | 路径参数 `user_id`（须大于 0） | 返回单个用户，不存在返回 404 |
| PUT | `/users/{user_id}` | 路径参数 `user_id` + 请求体 `UserUpdate`：`name`、`age` | 更新用户，不存在返回 404 |
| DELETE | `/users/{user_id}` | 路径参数 `user_id` | 删除用户，成功返回 204，不存在返回 404 |

> **提示**：Day 2 的数据保存在内存变量中，服务重启后用户列表会清空。

**用 curl 测试接口（Day 3）：**

```bash
# 根路径
curl http://127.0.0.1:8000/

# 健康检查
curl http://127.0.0.1:8000/health/

# 创建用户（重名返回 400）
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"name":"koko","age":20}'

# 分页查询
curl "http://127.0.0.1:8000/users/?page=1&size=10"

# 查询单个（不存在返回 404）
curl http://127.0.0.1:8000/users/1

# 更新（不存在返回 404）
curl -X PUT http://127.0.0.1:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"koko2","age":20}'

# 删除（成功返回 204，不存在返回 404）
curl -X DELETE http://127.0.0.1:8000/users/1
```

### Day 3 接口一览

| 方法 | 路径 | 参数 | 说明 |
| --- | --- | --- | --- |
| GET | `/` | 无 | 根路径，返回 `{"message": "FastAPI is running"}` |
| GET | `/health/` | 无 | 健康检查，返回 `{"status": "ok"}` |
| POST | `/users/` | 请求体 `UserCreate`：`name`（1～50 字符）、`age`（0～150） | 创建用户，成功返回 201，用户名已存在返回 400 |
| GET | `/users/` | 查询参数 `page`（默认 1，≥1）、`size`（默认 10，取值 1～100） | 分页返回用户列表 |
| GET | `/users/{user_id}` | 路径参数 `user_id` | 返回单个用户，不存在返回 404 |
| PUT | `/users/{user_id}` | 路径参数 `user_id`（须大于 0）+ 请求体 `UserUpdate`：`name`、`age` | 更新用户，不存在返回 404 |
| DELETE | `/users/{user_id}` | 路径参数 `user_id`（须大于 0） | 删除用户，成功返回 204，不存在返回 404 |

> **注意**：因为 `APIRouter` 的 `prefix="/users"` 配合 `@router.get("/")`，实际路径带上了结尾斜杠。请求不带斜杠的 `/users`、`/health` 会收到 307 重定向，`curl` 需要加 `-L` 才会自动跟随，浏览器和 `/docs` 页面不受影响。

> **说明**：每个请求的耗时都会打印在启动服务的控制台里，形如 `/users/: 0.0019s`。

> **提示**：Day 3 时数据保存在 `app/services/user_service.py` 的内存变量中，服务重启后会清空；Day 4 起已改为存入 MySQL，见下节。

**用 curl 测试接口（Day 4）：**

```bash
# 创建用户（重名返回 400，数据写入 users 表）
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"name":"koko","age":20}'

# 分页查询（读的就是数据库里的数据）
curl "http://127.0.0.1:8000/users/?page=1&size=10"

# 重启服务后再查一次，数据依然存在（验证已落库）
curl "http://127.0.0.1:8000/users/?page=1&size=10"
```

### Day 4 接口一览

Day 4 改的是数据层，接口路径、参数与状态码与 Day 3 完全一致（见上表），只有下面几处差异：

| 变化点 | 说明 |
| --- | --- |
| 数据存储 | 由内存变量改为 MySQL 的 `users` 表，服务重启后数据不丢失 |
| 数据库会话 | 每个接口通过 `db: Session = Depends(get_db)` 注入会话，请求结束自动关闭 |
| 路径参数 | `GET /users/{user_id}` 的 `user_id` 也要求大于 0（Day 3 未做校验） |
| 建表 | 应用启动时自动执行 `Base.metadata.create_all()` 创建缺失的表 |

> **提示**：Day 4 之后接口错误仍由路由层决定——找不到用户返回 404，创建重名返回 400，service 层只返回 `None` / `False`。

**用 curl 测试接口（Day 5）：**

```bash
# 注册（重名返回 400）
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"koko","password":"secret123","age":20}'

# 登录：注意是表单数据（application/x-www-form-urlencoded），不是 JSON
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=koko&password=secret123"
# 返回形如 {"access_token":"...","token_type":"bearer"}

# 用登录拿到的 token 访问受保护接口
curl http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### Day 5 接口一览

| 方法 | 路径 | 参数 | 说明 |
| --- | --- | --- | --- |
| POST | `/auth/register` | 请求体 `UserCreate`：`name`（1～50 字符）、`password`（6～128 字符）、`age`（0～150） | 注册用户，成功返回 201，用户名已存在返回 400 |
| POST | `/auth/login` | 表单 `username`、`password` | 登录，成功返回 `access_token` 与 `token_type`，账号或密码错误返回 401 |
| GET | `/auth/me` | 请求头 `Authorization: Bearer <token>` | 返回当前登录用户，token 无效 / 过期返回 401 |
| POST | `/users/` | 请求体 `UserCreate`（同注册，必须带 `password`） | 创建用户，成功 201，重名 400（与 `/auth/register` 功能重叠） |

> **说明**：`/auth/register`、`/auth/login`、`/auth/me` 的路径没有结尾斜杠，不存在 `/users/` 那样的 307 重定向问题。

> **提示**：Day 5 起 `UserCreate` 增加了 `password` 字段，Day 4 的创建用户示例需要补上 `"password":"secret123"`，否则返回 422；也可以直接改用 `/auth/register`。

> **提示**：在 `/docs` 页面点击右上角的 **Authorize**，填入用户名和密码，Swagger 会自动调用 `/auth/login` 并保存 token，之后再访问受保护接口会自动带上 `Authorization` 头。

> **提示**：token 默认 30 分钟后过期，过期后调用 `/auth/me` 返回 401，需要重新登录获取新 token。

> **⚠️ 安全提示**：`SECRET_KEY` 等同于签发 token 的私钥，泄露后任何人都能伪造登录状态。不要把它写进代码或提交到 Git，生产环境应换成足够长的随机值并妥善保管。

## 更新依赖

如果你新增了第三方库，请重新导出依赖清单：

```bash
pip freeze > requirements.txt
```

导出后请确认文件编码为 UTF-8（见上方「安装步骤」中的提示），否则 Git 会将其识别为二进制文件。
