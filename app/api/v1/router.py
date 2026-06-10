from fastapi import APIRouter
from app.api.v1.endpoints import stock

api_router = APIRouter()

# 挂载具体的业务路由，并设置前缀和标签（方便 Swagger UI 分类）
api_router.include_router(stock.router, prefix="/finance", tags=["Finance"])
# 如果有其他的，继续加：
# api_router.include_router(user.router, prefix="/users", tags=["Users"])
