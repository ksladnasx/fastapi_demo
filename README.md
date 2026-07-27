# FastAPI Demo

基于 FastAPI + SQLModel + MySQL 的简单用户 CRUD 示例项目。

## 项目结构

```text
app/
  api/
    users.py          # 用户路由，只负责 HTTP 请求和响应
  core/
    config.py         # 项目配置，比如数据库连接地址
  db/
    connection.py     # 数据库连接管理器，负责 engine、连接池配置和释放
    manager.py        # 数据库全局管理器，负责初始化、健康检查和 Session 入口
  models/
    user.py           # User 表映射 + UserDao 数据库操作类
  schemas/
    user.py           # API 请求/响应模型
    init.sql          # 初始化 users 表和测试数据
  main.py             # FastAPI 应用入口
run.py                # 本地启动脚本
```

## 分层说明

### `app/models/user.py`

这里放数据库相关模型和数据库操作类。

`User` 是 SQLModel 表映射：

```python
class User(UserBase, table=True):
    ...
```

带有 `table=True` 的类会映射到数据库表。本项目中它对应 MySQL 里的 `users` 表。

`UserDao` 是用户数据操作类：

```python
class UserDao:
    ...
```

用户的增删改查都定义在这里，比如：

```python
UserDao.create(...)
UserDao.get(...)
UserDao.list(...)
UserDao.update(...)
UserDao.delete(...)
```

这些方法内部统一使用：

```python
with get_sync_db_session() as session:
    ...
```

### `app/schemas/user.py`

这里放 API 的请求和响应模型，不直接映射数据库表。

- `UserCreate`：创建用户时的请求体
- `UserUpdate`：更新用户时的请求体
- `UserRead`：接口返回给前端的数据结构

路由里的 `response_model=UserRead` 表示接口响应会按照 `UserRead` 的字段进行输出。

### `app/api/users.py`

这里放用户相关路由。路由层不直接操作数据库，只调用 `UserDao`。

例如：

```python
return UserDao.create(user_data)
```

### `app/db/connection.py`

这里放数据库连接管理器 `DatabaseConnection`。

它负责：

- 延迟创建数据库 `engine`
- 配置连接池参数
- 释放数据库连接池
- 查看连接池状态

当前连接池配置在这里：

```python
create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_recycle=3600,
)
```

### `app/db/manager.py`

这里放数据库全局管理器 `DatabaseManager`。

它负责：

- 初始化数据库表
- 关闭数据库连接池
- 提供健康检查
- 提供连接池状态查看
- 提供统一的同步 Session 上下文

当前项目使用同步数据库会话：

```python
with get_sync_db_session() as session:
    ...
```

`db_manager.init_db()` 会在项目启动时根据 SQLModel 表模型自动创建表。

`db_manager.close()` 会在项目关闭时释放连接池。

`db_manager.health_check()` 可以用于检查数据库是否可用。

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
mysql --user=fastapi --password=fastapi --database=fastapi_demo --execute="SOURCE D:/Code/backend_demo/fastapi_demo/app/schemas/init.sql"
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
