# typing 里的两个工具：
# - Generic：让类支持泛型参数，比如 ApiResponse[int]、ApiResponse[User]
# - TypeVar：定义一个“类型占位符”T，使用时再替换成具体类型
from typing import TypeVar

# Pydantic 的基类，提供数据校验、序列化能力。
# FastAPI 常拿它当响应模型（response_model）。
from pydantic import BaseModel

# 定义一个类型变量 T。
# T 只是占位符，不代表具体类型；调用时才被替换。
# 比如 ApiResponse[int] 里的 T 就是 int。
T = TypeVar("T")


class ApiResponse[T](BaseModel):
    """
    统一 API 响应包装类。

    作用：给所有接口一个统一返回结构：
        {
            "code": 0,
            "data": <具体数据>,
            "message": "success"
        }

    泛型 T 表示 data 的实际类型：
        ApiResponse[User]     → data 是 User 或 None
        ApiResponse[list[User]] → data 是用户列表或 None
        ApiResponse[None]     → data 是 None
    """

    # 业务状态码，默认 0 表示成功。
    # 非 0 通常表示业务错误码（不是 HTTP 状态码）。
    code: int = 0

    # 真正的业务数据。
    # T | None 表示 data 可以是 T 类型，也可以是 None。
    # 默认 None，适合“成功但无返回数据”的场景。
    data: T | None = None

    # 提示信息，默认 "success"。
    # 出错时通常改成具体错误描述。
    message: str = "success"