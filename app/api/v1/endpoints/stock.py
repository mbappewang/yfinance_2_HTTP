from typing import List
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel

from app.schemas.response import BaseResponse, success
from app.handler.stock import history, get_isin, isin, get_history_metadata

router = APIRouter()


# ==========================================
# 1. 定义返回数据的结构 (Schema)
# ==========================================
class IsinData(BaseModel):
    symbol: str
    isin: str


class HistoryRecord(BaseModel):
    Date: str
    Open: float
    High: float
    Low: float
    Close: float
    Volume: int
    # 根据 actions=True，yfinance 可能会返回这俩字段，设为可选即可防报错
    Dividends: float = 0.0
    Stock_Splits: float = 0.0


# ==========================================
# 2. 路由定义
# ==========================================


@router.get("/{ticker}/get_isin", response_model=BaseResponse[IsinData])
async def get_stock_isin(
    ticker: str = Path(..., description="股票代码，例如 AAPL")
    ):
    try:
        isin_val = get_isin(ticker)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return success(data=IsinData(symbol=ticker, isin=isin_val))


# 【重点看这里】照搬 handler 参数的 API
@router.get("/{ticker}/history", response_model=BaseResponse[List[HistoryRecord]])
async def get_stock_history(
    ticker: str = Path(..., description="股票代码，例如 AAPL"),  # 从 URL 路径中获取
    # 以下全部自动转为 Query 参数，并保留默认值
    period: str = "1mo",
    interval: str = "1d",
    start: str | None = None,  # Python 3.10+ 的可选类型写法
    end: str | None = None,
    prepost: bool = False,
    actions: bool = True,
    auto_adjust: bool = True,
    back_adjust: bool = False,
    repair: bool = True,
    keepna: bool = False,
    rounding: bool = False,
    timeout: int = 10,
):
    try:
        # 直接透传给 handler
        data_list = history(
            symbol=ticker,
            period=period,
            interval=interval,
            start=start,
            end=end,
            prepost=prepost,
            actions=actions,
            auto_adjust=auto_adjust,
            back_adjust=back_adjust,
            repair=repair,
            keepna=keepna,
            rounding=rounding,
            timeout=timeout,
        )
        return success(data=data_list)

    except ValueError as e:
        # 如果参数填错了（比如 period 填了 "99mo"），这里会兜底拦截并抛出 400 错误
        raise HTTPException(status_code=400, detail=str(e))

