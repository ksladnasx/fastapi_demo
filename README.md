# FastAPI Demo

基于 FastAPI + SQLModel + MySQL 的 CRUD 示例项目。

## 数据库准备

请先确保以下 MySQL 配置就绪：

- **数据库名**：`fastapi_demo`
- **用户名**：`fastapi`
- **密码**：`fastapi`

### 初始化数据表

在已有的 `fastapi_demo` 数据库中创建表并插入测试数据：

```powershell
mysql --user=fastapi --password=fastapi --database=fastapi_demo --execute="SOURCE D:/Code/backend_demo/fastapi_demo/app/schemas/init.sql"
```

### 验证初始化结果

查看表结构和测试数据是否导入成功：

```powershell
mysql --user=fastapi --password=fastapi --database=fastapi_demo --execute="SHOW TABLES; SELECT * FROM users;"
```

## 运行项目

### 1. 激活虚拟环境

```powershell
.\.venv\Scripts\activate
```

### 2. 启动服务

```powershell
python run.py
```

### 3. 访问接口文档

启动成功后，打开浏览器访问：

```text
http://127.0.0.1:8000/docs
```

## API 接口列表

| 方法   | 路径               | 说明             |
| ------ | ------------------ | ---------------- |
| POST   | `/users/`          | 创建用户         |
| GET    | `/users/`          | 获取用户列表     |
| GET    | `/users/{user_id}` | 获取指定用户详情 |
| PUT    | `/users/{user_id}` | 更新用户信息     |
| DELETE | `/users/{user_id}` | 删除用户         |

## 快速测试

```powershell
# 创建用户
curl -X POST http://localhost:8000/users/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"张三\",\"email\":\"zhangsan@example.com\",\"full_name\":\"张三\",\"password\":\"123456\"}"

# 获取用户列表
curl http://localhost:8000/users/

# 获取指定用户
curl http://localhost:8000/users/1

# 更新用户
curl -X PUT http://localhost:8000/users/1 ^
  -H "Content-Type: application/json" ^
  -d "{\"full_name\":\"张先生\"}"

# 删除用户
curl -X DELETE http://localhost:8000/users/1
```

## 技术栈

- **FastAPI** - 现代 Web 框架
- **SQLModel** - ORM 和数据验证
- **MySQL** - 关系型数据库
- **PyMySQL** - MySQL 驱动
- **Uvicorn** - ASGI 服务器
