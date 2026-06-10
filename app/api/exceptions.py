from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.response import fail


def setup_exception_handlers(app: FastAPI):
    """
    统一为 FastAPI 实例注册所有的全局异常处理器
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=fail(code=exc.status_code, message=exc.detail).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        error_msg = f"参数校验失败: {exc.errors()}"
        return JSONResponse(
            status_code=422, content=fail(code=422, message=error_msg).model_dump()
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=fail(code=500, message=f"内部服务器错误: {str(exc)}").model_dump(),
        )
