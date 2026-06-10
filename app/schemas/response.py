from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

# 定义一个泛型变量 T
T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    code: int = 200  # 业务状态码，200 表示成功
    message: str = "success"  # 提示信息
    data: Optional[T] = None  # 实际数据，如果没有则为 None


# 快捷函数：用于生成成功响应
def success(data: Any = None, message: str = "success") -> BaseResponse:
    return BaseResponse(code=200, message=message, data=data)


# 快捷函数：用于生成失败响应（可选，通常通过异常抛出处理）
def fail(code: int, message: str, data: Any = None) -> BaseResponse:
    return BaseResponse(code=code, message=message, data=data)
