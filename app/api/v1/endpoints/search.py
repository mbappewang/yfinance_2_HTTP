from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.schemas.response import BaseResponse, success
from app.handler.searchHandler import lookup

router = APIRouter()


# ==========================================
# 1. 定义 请求 数据结构
# ==========================================
class LookupRequest(BaseModel):
    query: str = Field(
        ..., description="模糊搜索关键字，例如 Apple", examples=["Apple"]
    )
    type: str = Field(
        "all", description="过滤类型: all, stock, etf, cryptocurrency, etc."
    )
    count: int = Field(25, description="返回最大条数")
    timeout: int = Field(30, description="超时时间")


# ==========================================
# 2. 定义 真实 返回数据结构 (基于 2026 雅虎财经原生字段)
# ==========================================
class LookupRecord(BaseModel):
    symbol: str = Field(..., description="交易代码，例如 AAPL")
    shortName: Optional[str] = Field(None, description="公司或资产简称")
    exchange: str = Field(..., description="交易所代码，例如 NMS")
    quoteType: str = Field(
        ..., description="资产类型，例如 equity, cryptocurrency, etf"
    )
    rank: Optional[int] = Field(None, description="搜索匹配权重排名")
    regularMarketPrice: Optional[float] = Field(None, description="当前市场价格")
    regularMarketChange: Optional[float] = Field(None, description="今日价格变动绝对值")
    regularMarketPercentChange: Optional[float] = Field(
        None, description="今日涨跌幅百分比"
    )
    industryName: Optional[str] = Field(None, description="所属行业板块")
    industryLink: Optional[Optional[str]] = Field(None, description="行业板块雅虎链接")


# ==========================================
# 3. 路由定义
# ==========================================
@router.post("/lookup", response_model=BaseResponse[List[LookupRecord]])
async def search_market_lookup(request_data: LookupRequest):
    try:
        data_list = lookup(
            query=request_data.query,
            type=request_data.type,
            count=request_data.count,
            timeout=request_data.timeout,
        )
        return success(data=data_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
