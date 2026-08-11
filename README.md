# FastAPI Demo

基于 FastAPI + SQLModel + MySQL 的简单用户 CRUD 示例项目。

## 项目结构

```text
app/
├── api/
│   ├── users.py        # 处理用户 HTTP 接口
│   └── deps.py         # API 依赖示例，比如分页参数
├── core/
│   ├── config.py       # 全局配置
│   └── security.py     # 安全相关工具示例
├── db/
│   ├── connection.py   # 数据库连接管理器
│   ├── manager.py      # 数据库全局管理器
│   └── init.sql        # 数据库初始化脚本
├── models/
│   └── user.py         # 数据库表映射
├── schemas/
│   ├── user.py         # 用户请求/响应模型
│   └── response.py     # 统一响应模型
├── crud/
│   └── user.py         # 数据库操作
├── services/
│   └── user.py         # 用户业务逻辑
├── main.py             # FastAPI 应用入口
├── exceptions.py       # 统一业务异常
└── utils/
    └── common.py       # 公共工具函数
```

## 分层职责

| 层 | 职责 |
| --- | --- |
| `api` | 处理 HTTP 请求和响应 |
| `schemas` | 接口数据模型 |
| `services` | 业务逻辑 |
| `crud` | 数据库操作 |
| `models` | 数据库表映射 |
| `db` | 数据库连接 |
| `core` | 全局配置、安全 |
| `utils` | 公共工具 |

## 调用流程

```text
api/users.py
  -> services/user.py
    -> crud/user.py
      -> db/manager.py
        -> db/connection.py
```

## 统一响应格式

所有接口统一返回：

```json
{
  "code": 0,
  "data": {},
  "message": "success"
}
```

成功响应由 `app/utils/common.py` 中的 `success_response()` 生成。

响应模型定义在 `app/schemas/response.py`：

```python
class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    data: T | None = None
    message: str = "success"
```

用户接口示例：

```python
@router.post("/create_user", response_model=ApiResponse[UserRead])
def create_user(user_data: UserCreate):
    user = UserService.create_user(user_data)
    return success_response(data=user, message="User created successfully")
```

异常响应也使用同样格式：

```json
{
  "code": 404,
  "data": null,
  "message": "User not found"
}
```

## 分页参数

用户列表接口使用 `page` 和 `page_size`：

```text
GET /user/get_users?page=1&page_size=10
```

规则：

- `page >= 1`
- `page_size >= 1`
- `page_size <= 100`

## 登录认证与 JWT

项目使用登录接口签发 `access_token`，后续受保护接口需要在请求头中携带这个 token。

登录接口：

```text
POST /user/login
```

请求示例：

```json
{
  "username": "admin",
  "password": "admin123"
}
```

响应中的 `data.access_token` 就是访问令牌：

```json
{
  "code": 0,
  "data": {
    "access_token": "header.payload.signature",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "full_name": "Administrator",
      "is_active": true,
      "created_at": "2026-07-27T00:00:00",
      "updated_at": null
    }
  },
  "message": "Login successfully"
}
```

后续请求需要携带：

```http
Authorization: Bearer your_access_token
```

当前 JWT 由三部分组成：

```text
header.payload.signature
```

| 部分 | 说明 |
| --- | --- |
| `header` | 声明 token 类型和签名算法，例如 `typ=JWT`、`alg=HS256` |
| `payload` | 保存业务数据，目前包含 `sub` 用户 id 和 `exp` 过期时间 |
| `signature` | 使用 `SECRET_KEY` 对 `header.payload` 做 HMAC-SHA256 签名 |

签发逻辑在 `app/core/security.py` 的 `create_access_token()`：

1. 生成 `header`，声明使用 `HS256`。
2. 生成 `payload`，写入当前用户 id 和过期时间。
3. 对 `header` 和 `payload` 分别做 Base64URL 编码。
4. 使用 `SECRET_KEY` 对 `header.payload` 生成签名。
5. 拼成 `header.payload.signature` 返回给前端。

校验逻辑在 `app/core/security.py` 的 `decode_access_token()`：

1. 按 `.` 拆分 token，必须拆成三段。
2. 用相同的 `SECRET_KEY` 和算法重新计算签名。
3. 对比客户端传来的签名和后端重新计算的签名。
4. 解析 `header`，确认算法是 `HS256`，类型是 `JWT`。
5. 解析 `payload`，检查 `exp` 是否过期。
6. 从 `sub` 取出用户 id，再查询数据库确认用户存在且处于启用状态。

认证依赖在 `app/api/deps.py` 的 `get_current_user()`。接口参数中加入 `current_user: CurrentUserDep` 后，该接口就会要求请求头必须带合法 token。

当前公开接口：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/user/register` | 注册用户 |
| `POST` | `/user/login` | 用户登录 |

当前需要登录的接口：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/user/me` | 获取当前登录用户 |
| `POST` | `/user/create_user` | 创建用户 |
| `POST` | `/user/create_users` | 批量创建用户 |
| `GET` | `/user/get_users` | 获取用户列表 |
| `GET` | `/user/get/{user_id}` | 获取指定用户 |
| `PUT` | `/user/put/{user_id}` | 更新用户 |
| `DELETE` | `/user/del/{user_id}` | 删除用户 |

## 数据库配置

请确保你本地已经存在以下 MySQL 配置：

- 数据库名：`fastapi_demo`
- 用户名：`fastapi`
- 密码：`fastapi`

项目默认连接地址在 `app/core/config.py`：

```text
mysql+pymysql://fastapi:fastapi@localhost:3306/fastapi_demo?charset=utf8mb4
```

## 初始化数据库表

在已有的 `fastapi_demo` 数据库中创建 `users` 表并插入测试数据：

```powershell
mysql --user=fastapi --password=fastapi --database=fastapi_demo --execute="SOURCE D:/Code/backend_demo/fastapi_demo/app/db/init.sql"
```

验证初始化结果：

```powershell
mysql --user=fastapi --password=fastapi --database=fastapi_demo --execute="SHOW TABLES; SELECT * FROM users;"
```

## 启动项目

激活虚拟环境：

```powershell
.\.venv\Scripts\activate
```

启动服务：

```powershell
python run.py
```

访问接口文档：

```text
http://127.0.0.1:8000/docs
```

## API 列表

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/user/register` | 注册用户 |
| `POST` | `/user/login` | 用户登录 |
| `GET` | `/user/me` | 获取当前登录用户 |
| `POST` | `/user/create_user` | 创建用户 |
| `POST` | `/user/create_users` | 批量创建用户 |
| `GET` | `/user/get_users` | 获取用户列表 |
| `GET` | `/user/get/{user_id}` | 获取指定用户 |
| `PUT` | `/user/put/{user_id}` | 更新用户 |
| `DELETE` | `/user/del/{user_id}` | 删除用户 |
| `GET` | `/recruitment/jobs` | 查询已入库的招聘信息 |
| `POST` | `/recruitment/import/givemeoc` | 爬取 GivemeOC 并写入数据库 |

初始化脚本内置示例账号：

| 用户名 | 密码 |
| --- | --- |
| `admin` | `admin123` |
| `testuser` | `test123` |

## GivemeOC 招聘信息导入

爬虫需要使用你自己浏览器里的登录 Cookie 和页面 nonce。不要把这些值写进代码，放到项目根目录的 `.env` 文件即可：

```env
GIVEMEOC_COOKIE=你的完整 Cookie
GIVEMEOC_NONCE=页面请求里的 nonce
GIVEMEOC_REQUEST_DELAY_SECONDS=0.4
GIVEMEOC_TIMEOUT_SECONDS=20
```

命令行导入 30 页：

```powershell
.\.venv\Scripts\python.exe tools\import_givemeoc_jobs.py --pages 30 --start-page 1
```

也可以在服务启动后通过接口触发。这个接口会使用你的私有 Cookie，需要先登录并携带 `Authorization`：

```text
POST http://127.0.0.1:8000/recruitment/import/givemeoc?pages=30&start_page=1
```

前端页面在 `frontend/index.html`，打开后可以查询：

```text
GET /recruitment/jobs?page=1&page_size=20&keyword=&location=&progress_status=
```
