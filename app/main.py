from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.v1.router import api_router
from app.api.exceptions import setup_exception_handlers
from app.core.config import settings


# 1. 定义 lifespan 上下文管理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ==================================
    # yield 之前的代码：相当于 "startup" 事件
    # ==================================
    print(f"🚀 服务已启动，端口: {settings.base.port}")
    print(f"📊 当前日志级别: {settings.base.log_level}")

    # 比如在这里初始化数据库连接、加载机器学习模型等
    # db_connection = connect_to_db()

    yield  # 挂起函数，将控制权交还给 FastAPI，此时应用开始接收请求

    # ==================================
    # yield 之后的代码：相当于 "shutdown" 事件
    # ==================================
    print("🛑 服务正在关闭，清理资源...")
    # 比如在这里关闭数据库连接
    # db_connection.close()


# 2. 将 lifespan 传递给 FastAPI 实例
app = FastAPI(
    title=f"My App {settings.base.version}",
    lifespan=lifespan,  # 绑定生命周期
)


# 2. 初始化 FastAPI 实例
app = FastAPI(
    title="YFinance to Golang API", version=settings.base.version, lifespan=lifespan
)

# 注入全局异常拦截
setup_exception_handlers(app)

# 3. 挂载路由 (将 v1 的所有路由挂载到 /api/v1 下)
app.include_router(api_router, prefix="/api/v1")


