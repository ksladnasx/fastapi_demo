# FastAPI Demo

基于 FastAPI + SQLModel + MySQL 的简单用户 CRUD 示例项目。

## 项目结构

```text
app/
│
├── api/
│   ├── users.py        # 处理用户 HTTP 接口
│   └── deps.py         # API 依赖示例，比如分页参数
│
├── core/
│   ├── config.py       # 全局配置
│   └── security.py     # 安全相关工具示例
│
├── db/
│   ├── connection.py   # 数据库连接管理器
│   ├── manager.py      # 数据库全局管理器
│   └── init.sql        # 数据库初始化脚本
│
├── models/
│   └── user.py         # 数据库表映射
│
├── schemas/
│   └── user.py         # API 请求/响应模型
│
├── crud/
│   └── user.py         # 数据库操作
│
├── services/
│   └── user.py         # 用户业务逻辑
│
├── main.py             # FastAPI 应用入口
│
├── exceptions.py       # 统一业务异常
│
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

当前用户接口的调用链路是：

```text
api/users.py
  -> services/user.py
    -> crud/user.py
      -> db/manager.py
        -> db/connection.py
```

### API 层

`app/api/users.py` 只处理 HTTP 层逻辑，比如路由、状态码和请求参数。

示例：

```python
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate):
    return UserService.create_user(user_data)
```

`app/api/deps.py` 提供了一个简单分页依赖：

```python
pagination: PaginationDep
```

### Service 层

`app/services/user.py` 负责业务规则，比如：

- 用户名不能重复
- 邮箱不能重复
- 查询不到用户时抛出业务异常
- 创建/更新前统一处理邮箱格式

示例：

```python
if UserDao.get_by_email(user_data.email):
    raise BadRequestException("Email already registered")
```

### CRUD 层

`app/crud/user.py` 只负责数据库读写，不处理 HTTP，也尽量不写业务规则。

示例：

```python
with get_sync_db_session() as session:
    user = session.get(User, user_id)
```

### Model 层

`app/models/user.py` 是 SQLModel 表映射。

```python
class User(UserBase, table=True):
    __tablename__ = "users"
```

带有 `table=True` 的类会映射到数据库表。

### Schema 层

`app/schemas/user.py` 是 API 请求/响应模型。

- `UserCreate`：创建用户请求体
- `UserUpdate`：更新用户请求体
- `UserRead`：接口响应模型

路由里的 `response_model=UserRead` 表示返回数据会按 `UserRead` 输出。

### DB 层

`app/db/connection.py` 负责创建和释放数据库 `engine`，并配置连接池。

`app/db/manager.py` 负责统一管理数据库生命周期：

- `db_manager.init_db()`：启动时初始化表
- `db_manager.close()`：关闭时释放连接池
- `db_manager.health_check()`：数据库健康检查
- `get_sync_db_session()`：提供同步 Session 上下文

### Core 和 Utils

`app/core/security.py` 提供了一个简单安全工具示例：

```python
verify_api_key(api_key, expected_api_key)
```

`app/utils/common.py` 提供了公共工具函数示例：

```python
normalize_email(email)
```

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
| `POST` | `/users/` | 创建用户 |
| `GET` | `/users/` | 获取用户列表 |
| `GET` | `/users/{user_id}` | 获取指定用户 |
| `PUT` | `/users/{user_id}` | 更新用户 |
| `DELETE` | `/users/{user_id}` | 删除用户 |
