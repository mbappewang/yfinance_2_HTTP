from fastapi import APIRouter
from app.api.v1.endpoints import stock, search

api_router = APIRouter()

# 挂载具体的业务路由，并设置前缀和标签（方便 Swagger UI 分类）
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(stock.router, prefix="/stock", tags=["Stock"])
