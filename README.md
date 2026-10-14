# FastAPI Demo

这是一个用于学习 FastAPI 后端认证流程的小项目，包含：

- 用户注册、登录、查询当前用户
- Authorization Bearer Token 模式
- HttpOnly Cookie 模式
- 前端页面对比演示 Token 和 Cookie 的区别
- SQLModel + MySQL 数据库示例

## 启动项目

```powershell
fastapi dev
```

启动后访问：

- API 文档：http://127.0.0.1:8000/docs
- 前端页面：建议用本地静态服务打开，而不是直接双击 HTML

打开前端的推荐方式：

```powershell
cd frontend
python -m http.server 5500
```

然后访问：

```text
http://127.0.0.1:5500
```

前端页面里的 API 地址建议保持为：

```text
http://127.0.0.1:8000
```

这样前端页面和 API 都使用 `127.0.0.1`，更方便观察浏览器 Cookie。

## 数据库配置

默认数据库连接在 `app/core/config.py`：

```text
mysql+pymysql://fastapi:123456@localhost:3306/fastapi_demo?charset=utf8mb4
```

含义是：

- 数据库：`fastapi_demo`
- 用户名：`fastapi`
- 密码：`123456`
- 主机：`localhost`
- 端口：`3306`

如果你的数据库配置不同，可以在 `.env` 中覆盖：

```env
DATABASE_URL=mysql+pymysql://用户名:密码@localhost:3306/fastapi_demo?charset=utf8mb4
```

初始化数据库表和测试用户：

```powershell
mysql --user=fastapi --password=123456 --database=fastapi_demo --execute="SOURCE D:/Code/backend_demo/fastapi_demo/app/db/init.sql"
```

内置测试账号：

| 用户名 | 密码 |
| --- | --- |
| `admin` | `admin123` |
| `testuser` | `test123` |

## Token 模式怎么理解

接口：

```text
POST /user/login
```

登录成功后，后端返回：

```json
{
  "access_token": "header.payload.signature",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {}
}
```

前端需要自己保存 `access_token`，之后请求受保护接口时手动加请求头：

```http
Authorization: Bearer your_access_token
```

例如：

```text
GET /user/me
```

后端通过 `app/api/deps.py` 里的 `get_current_user()` 解析请求头并识别用户。

## Cookie 模式怎么理解

接口：

```text
POST /cookie/login
```

登录成功后，后端不会要求前端保存 token，而是通过响应头告诉浏览器保存 Cookie：

```http
Set-Cookie: fastapi_demo_session=...; HttpOnly; Path=/; SameSite=Lax
```

之后前端请求：

```text
GET /cookie/me
```

只要 `fetch` 设置了：

```js
credentials: "include"
```

浏览器就会自动带上 Cookie。后端通过 `app/api/deps.py` 里的 `get_current_user_from_cookie()` 从 Cookie 中识别用户。

退出登录接口：

```text
POST /cookie/logout
```

它会让浏览器删除会话 Cookie。

## Cookie 演示接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/cookie/login` | 登录并设置 HttpOnly 会话 Cookie |
| `GET` | `/cookie/me` | 从 Cookie 中读取当前用户 |
| `POST` | `/cookie/logout` | 删除会话 Cookie |
| `POST` | `/cookie/visible` | 设置一个非 HttpOnly Cookie，方便用 `document.cookie` 观察 |
| `DELETE` | `/cookie/visible` | 删除可见 Cookie |

## 普通用户接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/user/register` | 注册用户 |
| `POST` | `/user/login` | 用户登录，返回 access_token |
| `GET` | `/user/me` | 通过 Authorization Token 获取当前用户 |
| `POST` | `/user/create_user` | 创建用户 |
| `POST` | `/user/create_users` | 批量创建用户 |
| `GET` | `/user/get_users` | 获取用户列表 |
| `GET` | `/user/get/{user_id}` | 获取指定用户 |
| `PUT` | `/user/put/{user_id}` | 更新用户 |
| `DELETE` | `/user/del/{user_id}` | 删除用户 |

## 这次已移除的内容

之前项目中的 GivemeOC 招聘爬虫、招聘数据模型、招聘接口和前端招聘面板已经删除，项目现在更聚焦于认证学习。
