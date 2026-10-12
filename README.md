# FastAPI 项目练习（Week 2）

这是一个 FastAPI 学习练习项目，承接 Week 1 的 Python 基础练习（见 `python-test`），按“每日一个独立模块”的方式组织。每天的内容作为独立的迷你应用存放在 `src/` 下，共享同一个虚拟环境。

## 项目内容

### Day 1：FastAPI 基础（路由、参数与请求体）
- 创建 `FastAPI` 应用实例，理解 `app = FastAPI()` 与装饰器路由（`@app.get` / `@app.post`）
- 路径参数：`/users/{user_id}` 配合类型注解 `user_id: int`，自动完成参数解析与类型转换
- 查询参数：`/search?keyword=&page=&size=`，带默认值的参数（`page: int = 1`）变为可选
- 请求体：使用 Pydantic `BaseModel` 定义 `UserCreate`（name / age），POST 提交 JSON 自动校验并解析
- 通过 `uvicorn` 启动服务，使用内置交互式文档（`/docs`、`/redoc`）调试接口
- `day1_test.py` 中已用注释预留商品接口（`/products/{product_id}`、`/products?category=`、`ProductCreate` 的 `Field(gt=0)` 校验）作为后续练习

### Day 2：内存 CRUD（分页、响应模型与异常处理）
- 用模块级列表 `users` 配合自增变量 `next_id` 作为存储，数据只存在内存中，服务重启即清空；`find_user(user_id)` 抽出按 ID 查找的逻辑
- 按用途拆分 Pydantic 模型：`UserCreate`（创建入参校验）、`UserResponse`（统一响应结构）、`UserUpdate`（更新入参）
- 用 `Field` 做字段级约束：`name` 限制 `min_length=1 / max_length=50`，`age` 限制 `gt=0 / lt=150`，非法值由 FastAPI 自动返回 422
- 分页查询：`/users?page=&size=` 使用 `Query(default=1, ge=1, le=100, description="页码")`，通过列表切片 `users[start:end]` 返回当页数据
- 路径参数校验：`/users/{user_id}` 使用 `Path(gt=0)`，要求 ID 为正整数
- 每个接口用 `response_model` 声明响应结构，创建接口设置 `status_code=201`
- 异常处理：查找、更新、删除找不到用户时抛出 `HTTPException(status_code=404, detail="用户未找到")`；创建时用户名重复返回 400
- 练习状态码语义：创建成功 201、删除成功 204、资源不存在 404、用户名已存在 400

## 项目结构

```text
FastAPI-week2/
├── .env                  # 本地私有配置，存放 Token / API Key（不提交至 Git）
├── .env_example          # 环境变量模板（可提交至 Git）
├── .gitattributes
├── .gitignore
├── requirements.txt
├── README.md
├── conftest.py           # 空文件，让 pytest 把项目根加入 sys.path
├── data/                 # 练习数据目录（暂为空）
├── output/               # 数据保存目录（暂为空）
├── tests/                # 测试代码目录（暂为空）
└── src/
    ├── __init__.py
    ├── day1_test.py      # Day1 入口：基础路由 / 路径参数 / 查询参数 / 请求体
    ├── day2_test.py      # Day2 入口：内存 CRUD / 分页 / 响应模型与异常处理
    └── main.py           # 预留的主入口文件（暂为空）
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

> **提示**：Windows PowerShell 的重定向默认生成 UTF-16 编码的文件，可能导致其他环境读取异常。可改用 `pip freeze | Out-File -Encoding utf8 requirements.txt`。

## 配置说明

根目录的 `.env_example` 提供了环境变量模板，将其中内容复制为 `.env` 后填入真实值：

```bash
cp .env_example .env
```

```env
GITHUB_TOKEN=
OPENAI_API_KEY=
```

- Day 1 / Day 2 暂未使用上述变量，此处为后续接入 GitHub / OpenAI 等外部接口预留。
- 代码中通过 `os.getenv("XXX")` 读取配置。
- 确认 `.gitignore` 中包含 `.env`，防止密钥被提交至 Git；`.env_example` 只放变量名、不放真实值，可以提交。

> **⚠️ 安全提示**：Token 和 API Key 等同于密码，请勿直接写在代码中，也不要上传至 GitHub。

## 运行方式

**启动 Day 1 服务：**

```bash
python -m uvicorn src.day1_test:app --reload
```

**启动 Day 2 服务：**

```bash
python -m uvicorn src.day2_test:app --reload
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
curl -X DELETE http://127.0.0.1:8000/user/1
```

### Day 2 接口一览

| 方法 | 路径 | 参数 | 说明 |
| --- | --- | --- | --- |
| POST | `/users` | 请求体 `UserCreate`：`name`（1～50 字符）、`age`（0～150） | 创建用户，成功返回 201，用户名已存在返回 400 |
| GET | `/users` | 查询参数 `page`（默认 1）、`size`（默认 10），取值 1～100 | 分页返回用户列表 |
| GET | `/users/{user_id}` | 路径参数 `user_id`（须大于 0） | 返回单个用户，不存在返回 404 |
| PUT | `/users/{user_id}` | 路径参数 `user_id` + 请求体 `UserUpdate`：`name`、`age` | 更新用户，不存在返回 404 |
| DELETE | `/user/{user_id}` | 路径参数 `user_id` | 删除用户，成功返回 204，不存在返回 404 |

> **注意**：删除接口的路径目前为 `/user/{user_id}`（单数），与其余接口的 `/users/...` 命名不一致，属于待修正项，调用时以实际路径为准。

> **提示**：Day 2 的数据保存在内存变量中，服务重启后用户列表会清空。

## 更新依赖

如果你新增了第三方库，请重新导出依赖清单：

```bash
pip freeze > requirements.txt
```
