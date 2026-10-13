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
├── app/                       # 主应用（Day 3 分层结构）
│   ├── __init__.py
│   ├── main.py                # 应用入口：创建 FastAPI 实例、注册中间件与路由
│   ├── api/                   # 路由层：只处理 HTTP 请求与响应
│   │   ├── __init__.py
│   │   ├── health.py          # /health/ 健康检查
│   │   └── users.py           # /users 用户相关接口
│   ├── core/                  # 基础设施层
│   │   ├── __init__.py
│   │   ├── config.py          # 配置类，从 .env 读取 app_name / debug
│   │   └── middleware.py      # 请求耗时中间件
│   ├── schemas/               # 数据模型层
│   │   ├── __init__.py
│   │   └── user.py            # UserCreate / UserUpdate / UserResponse
│   └── services/              # 业务逻辑层
│       ├── __init__.py
│       └── user_service.py    # 内存 CRUD 的具体实现
│
└── tests/                     # 每日练习代码
    ├── day1_test.py           # Day1：基础路由 / 路径参数 / 查询参数 / 请求体
    ├── day2_test.py           # Day2：内存 CRUD / 分页 / 响应模型与异常处理
    ├── day3_depends_demo.py   # Day3：Depends 依赖注入练习（应用实例变量名为 router）
    └── day3_time_demo.py      # Day3：中间件练习
```

## 环境
- Python 3.13.14
- 操作系统：Windows 11

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
```

- **Day 3 已使用**：`APP_NAME`、`DEBUG`，由 `app/core/config.py` 的 `Settings` 类读取，分别对应字段 `app_name`、`debug`（`pydantic-settings` 默认大小写不敏感，`.env` 里写大写、代码里用小写即可）。
- `GITHUB_TOKEN`、`DATABASE_URL`、`SECRET_KEY` 暂未使用，为后续接入 GitHub / 数据库 / 鉴权预留。
- 也可以继续用 `os.getenv("XXX")` 读取配置，两种方式并存。
- 确认 `.gitignore` 中包含 `.env`，防止密钥被提交至 Git；`.env_example` 只放变量名、不放真实值，可以提交。

> **⚠️ 安全提示**：Token 和 API Key 等同于密码，请勿直接写在代码中，也不要上传至 GitHub。

> **注意**：`SettingsConfigDict(env_file=".env")` 中的路径是相对路径，相对**当前工作目录**解析。因此启动服务时请在项目根目录执行下面的命令，否则 `.env` 会读取不到（此时会静默使用代码里的默认值）。

## 运行方式

**启动主应用（Day 3 结构）：**

```bash
python -m uvicorn app.main:app --reload
```

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
  -d '{"name":"koko","age":23}'

# 分页查询
curl "http://127.0.0.1:8000/users/?page=1&size=10"

# 查询单个（不存在返回 404）
curl http://127.0.0.1:8000/users/1

# 更新（不存在返回 404）
curl -X PUT http://127.0.0.1:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"koko2","age":24}'

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

> **提示**：数据仍然保存在 `app/services/user_service.py` 的内存变量中，服务重启后会清空。数据持久化留待后续实现。

## 更新依赖

如果你新增了第三方库，请重新导出依赖清单：

```bash
pip freeze > requirements.txt
```

导出后请确认文件编码为 UTF-8（见上方「安装步骤」中的提示），否则 Git 会将其识别为二进制文件。
