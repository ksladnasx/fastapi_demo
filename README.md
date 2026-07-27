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
| `POST` | `/user/create_user` | 创建用户 |
| `POST` | `/user/create_users` | 批量创建用户 |
| `GET` | `/user/get_users` | 获取用户列表 |
| `GET` | `/user/get/{user_id}` | 获取指定用户 |
| `PUT` | `/user/put/{user_id}` | 更新用户 |
| `DELETE` | `/user/del/{user_id}` | 删除用户 |
