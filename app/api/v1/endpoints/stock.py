from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.schemas.response import BaseResponse, success
from app.handler.stockHandler import (
    get_isin,
    history,
    get_history_metadata,
    get_dividends,
    get_splits,
    get_actions,
    get_capital_gains,
    get_shares_full,
    get_info,
    get_fast_info,
    get_news,
)

router = APIRouter()

# ==========================================
# 1. 定义 请求 数据结构 (Request Schemas)
# ==========================================


class IsinRequest(BaseModel):
    ticker: str = Field(..., description="股票代码，例如 AAPL", examples=["AAPL"])


class HistoryRequest(BaseModel):
    ticker: str = Field(..., description="股票代码，例如 AAPL", examples=["AAPL"])
    period: str = "max"
    interval: str = "1d"
    start: str = ""
    end: str = ""
    prepost: bool = False
    actions: bool = True
    auto_adjust: bool = True
    back_adjust: bool = False
    repair: bool = False
    keepna: bool = False
    rounding: bool = False
    timeout: int = 10


class MetadataRequest(BaseModel):
    ticker: str = Field(..., description="股票代码，例如 AAPL", examples=["AAPL"])


class DividendsRequest(BaseModel):
    ticker: str = Field(..., description="股票代码，例如 AAPL", examples=["AAPL"])
    period: str = "max"


class SplitsRequest(BaseModel):
    ticker: str = Field(..., description="股票代码，例如 AAPL", examples=["AAPL"])
    period: str = "max"


class ActionsRequest(BaseModel):
    ticker: str = Field(..., description="股票代码，例如 AAPL", examples=["AAPL"])
    period: str = "max"


class CapitalGainsRequest(BaseModel):
    ticker: str = Field(..., description="股票代码，例如 AAPL", examples=["AAPL"])
    period: str = "max"


class SharesFullRequest(BaseModel):
    ticker: str = Field(..., description="股票代码，例如 AAPL", examples=["AAPL"])
    start: str = ""
    end: str = ""


class InfoRequest(BaseModel):
    ticker: str = Field(..., description="股票代码，例如 AAPL", examples=["AAPL"])


class FastInfoRequest(BaseModel):
    ticker: str = Field(..., description="股票代码，例如 AAPL", examples=["AAPL"])


class NewsRequest(BaseModel):
    ticker: str = Field(..., description="股票代码，例如 AAPL", examples=["AAPL"])
    count: int = 10
    tab: str = Field("news", description="可选值: 'news', 'all', 'press releases'", examples=["news"])


# ==========================================
# 2. 定义 返回 数据结构 (Response Schemas)
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
    Dividends: float = 0.0
    Stock_Splits: float = 0.0


class DividendRecord(BaseModel):
    Date: str
    Dividends: float


class SplitRecord(BaseModel):
    Date: str
    SplitRatio: float


class ActionRecord(BaseModel):
    Date: str
    Dividends: float
    SplitRatio: float


class CapitalGainRecord(BaseModel):
    Date: str
    CapitalGains: float


class ShareRecord(BaseModel):
    Date: str
    Shares: int


class NewsRecord(BaseModel):
    uuid: str
    title: str
    publisher: str
    link: str
    providerPublishTime: int
    type: str
    relatedTickers: List[str]


# ==========================================
# 3. 路由定义 (POST 接口)
# ==========================================


@router.post("/get_isin", response_model=BaseResponse[IsinData])
async def get_stock_isin(request_data: IsinRequest):
    try:
        ticker = request_data.ticker
        isin_val = get_isin(ticker)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return success(data=IsinData(symbol=ticker, isin=isin_val))


@router.post("/history", response_model=BaseResponse[List[HistoryRecord]])
async def get_stock_history(request_data: HistoryRequest):
    try:
        data_list = history(
            symbol=request_data.ticker,
            period=request_data.period,
            interval=request_data.interval,
            start=request_data.start,
            end=request_data.end,
            prepost=request_data.prepost,
            actions=request_data.actions,
            auto_adjust=request_data.auto_adjust,
            back_adjust=request_data.back_adjust,
            repair=request_data.repair,
            keepna=request_data.keepna,
            rounding=request_data.rounding,
            timeout=request_data.timeout,
        )
        return success(data=data_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/get_history_metadata", response_model=BaseResponse[dict])
async def get_stock_history_metadata(request_data: MetadataRequest):
    try:
        data = get_history_metadata(request_data.ticker)
        return success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/get_dividends", response_model=BaseResponse[List[DividendRecord]])
async def get_stock_dividends(request_data: DividendsRequest):
    try:
        data_list = get_dividends(symbol=request_data.ticker, period=request_data.period)
        return success(data=data_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/get_splits", response_model=BaseResponse[List[SplitRecord]])
async def get_stock_splits(request_data: SplitsRequest):
    try:
        data_list = get_splits(symbol=request_data.ticker, period=request_data.period)
        return success(data=data_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/get_actions", response_model=BaseResponse[List[ActionRecord]])
async def get_stock_actions(request_data: ActionsRequest):
    try:
        data_list = get_actions(symbol=request_data.ticker, period=request_data.period)
        return success(data=data_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/get_capital_gains", response_model=BaseResponse[List[CapitalGainRecord]])
async def get_stock_capital_gains(request_data: CapitalGainsRequest):
    try:
        data_list = get_capital_gains(symbol=request_data.ticker, period=request_data.period)
        return success(data=data_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/get_shares_full", response_model=BaseResponse[List[ShareRecord]])
async def get_stock_shares_full(request_data: SharesFullRequest):
    try:
        data_list = get_shares_full(
            symbol=request_data.ticker,
            start=request_data.start,
            end=request_data.end,
        )
        return success(data=data_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/get_info", response_model=BaseResponse[dict])
async def get_stock_info_detail(request_data: InfoRequest):
    try:
        data = get_info(request_data.ticker)
        return success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/get_fast_info", response_model=BaseResponse[dict])
async def get_stock_fast_info_detail(request_data: FastInfoRequest):
    try:
        data = get_fast_info(request_data.ticker)
        return success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/get_news", response_model=BaseResponse[List[dict]])
async def get_stock_news_list(request_data: NewsRequest):
    try:
        data_list = get_news(
            symbol=request_data.ticker,
            count=request_data.count,
            tab=request_data.tab,
        )
        return success(data=data_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
