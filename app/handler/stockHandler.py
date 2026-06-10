import math
from typing import Any, List, cast
import yfinance as yf
import pandas as pd


def _to_json_compatible(value: Any):
    if isinstance(value, pd.DataFrame):
        return _to_json_compatible(value.reset_index().to_dict(orient="records"))

    if isinstance(value, pd.Series):
        return _to_json_compatible(value.reset_index().to_dict(orient="records"))

    if isinstance(value, dict):
        return {str(k): _to_json_compatible(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_to_json_compatible(item) for item in value]

    if value is pd.NaT:
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if isinstance(value, pd.Timedelta):
        return value.isoformat()

    if isinstance(value, float) and math.isnan(value):
        return None

    item = getattr(value, "item", None)
    if callable(item):
        try:
            return _to_json_compatible(item())
        except ValueError:
            pass

    return value


def get_isin(symbol: str) -> str:
    try:
        result = yf.Ticker(symbol).get_isin()

        if not result or result == "-":
            # 1. 这里是我们主动抛出的业务错误
            raise ValueError(f"未找到股票 {symbol} 的 ISIN 数据")

        return result

    except ValueError:
        # 2. 拦截到我们自己抛出的 ValueError，直接往外扔，不套娃
        raise

    except Exception as e:
        # 3. 拦截到真正的、意料之外的报错（比如断网了），再进行包装
        raise ValueError(f"请求 {symbol} 时发生未知异常: {str(e)}")

def history(
    symbol: str,
    period: str = "max",
    interval: str = "1d",
    start="",
    end="",
    prepost=False,
    actions=True,
    auto_adjust=True,
    back_adjust=False,
    repair=False,
    keepna=False,
    rounding=False,
    timeout=10,
) -> List[dict]:
    try:
        # 1. 完整透传所有参数给 yfinance
        df: pd.DataFrame = yf.Ticker(symbol).history(
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
            raise_errors=False,
        )

        # 2. 核心避坑：yfinance 在找不到股票或参数错误时，往往不报错，而是返回一个空的 DataFrame
        if df.empty:
            raise ValueError(f"未找到股票 {symbol} 的历史K线数据，请检查代码或时间参数")

        # 3. 将 Date 或 Datetime 索引转换为普通的列
        df = df.reset_index()

        # 4. 转换时间类型为字符串（如果不转，Pandas 的 Timestamp 对象在转成字典后可能引发序列化问题，对 Golang 也不友好）
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                # 自动将本地时区时间转换为标准的字符串格式，例如 "2026-03-31 00:00:00"
                df[col] = df[col].astype(str)

        # 5. 转换为 List[Dict] 格式返回
        # 结果长这样：[{"Date": "2026-03-30", "Open": 150.0, "High": 155.0, ...}, ...]
        return df.to_dict(orient="records")

    except ValueError:
        # 拦截到我们自己抛出的 ValueError，直接往外扔
        raise

    except Exception as e:
        # 拦截到真正的系统异常（如网络超时、yfinance 内部崩溃）
        raise ValueError(f"请求 {symbol} 历史数据时发生未知异常: {str(e)}")


def get_history_metadata(symbol: str) -> dict[str, Any]:
    try:
        # 【关键修复】：加上括号 ()，让它真正去执行并获取数据
        results = yf.Ticker(symbol).get_history_metadata()

        # 兜底校验（可选）：如果 yfinance 没找到数据返回了空字典
        if not results:
            raise ValueError(f"未找到股票 {symbol} 的历史元数据")

        return cast(dict[str, Any], _to_json_compatible(results))

    except ValueError:
        # 放行主动抛出的业务错误
        raise
    except Exception as e:
        # 包装未知异常
        raise ValueError(f"获取 {symbol} 元数据时发生未知异常: {str(e)}")


def get_dividends(symbol: str, period: str = "max") -> List[dict]:
    try:
        # 1. 获取分红数据 (返回 Series)
        dividends_series = yf.Ticker(symbol).get_dividends(period=period)

        # 如果没有分红记录，返回空列表而不是报错
        if dividends_series.empty:
            return []

        # 2. 将 Series 转换为 DataFrame，方便处理日期索引
        df = dividends_series.reset_index()

        # 3. 将时间格式强转为字符串 (例如 "2024-05-10")
        df["Date"] = df["Date"].astype(str)

        # 4. 转换为 List[Dict] 格式
        # 结果长这样: [{"Date": "2024-05-10 00:00:00-04:00", "Dividends": 0.25}, ...]
        return df.to_dict(orient="records")

    except Exception as e:
        raise ValueError(f"获取 {symbol} 分红数据时发生异常: {str(e)}")

def get_splits(symbol: str, period: str = "max") -> List[dict]:
    try:
        # 1. 获取拆股数据 (返回 Series)
        splits_series = yf.Ticker(symbol).get_splits(period=period)

        # 2. 兜底：如果没有发生过拆股，返回空列表
        if splits_series.empty:
            return []

        # 3. 将 Series 转换为 DataFrame
        df = splits_series.reset_index()

        # 4. 时间格式清洗
        df["Date"] = df["Date"].astype(str)

        # 因为返回的列名默认叫 "Stock Splits"，带有空格，在转 JSON 和 Golang 结构体时有点麻烦
        # 建议在这里重命名一下列名，使其更符合规范
        df.rename(columns={"Stock Splits": "SplitRatio"}, inplace=True)

        # 5. 转换为 List[Dict] 格式
        # 结果长这样: [{"Date": "2020-08-31 00:00:00-04:00", "SplitRatio": 4.0}, ...]
        return df.to_dict(orient="records")

    except Exception as e:
        raise ValueError(f"获取 {symbol} 拆股数据时发生异常: {str(e)}")

def get_actions(symbol: str, period: str = "max") -> List[dict]:
    try:
        # 1. 获取公司行动数据 (返回 DataFrame)
        actions_df = yf.Ticker(symbol).get_actions(period=period)

        # 2. 兜底校验
        if actions_df.empty:
            return []

        # 3. 将日期索引变成普通列
        df = actions_df.reset_index()

        # 4. 时间格式清洗为字符串
        df["Date"] = df["Date"].astype(str)

        # 5. 重命名列名，消除空格，方便 Golang 定义结构体
        df.rename(columns={"Stock Splits": "SplitRatio"}, inplace=True)

        # 6. 转换为 List[Dict] 格式
        # 结果长这样: [{"Date": "2014-06-09...", "Dividends": 0.0, "SplitRatio": 7.0}, ...]
        return df.to_dict(orient="records")

    except Exception as e:
        raise ValueError(f"获取 {symbol} 公司行动数据时发生异常: {str(e)}")

def get_capital_gains(symbol: str, period: str = "max") -> List[dict]:
    try:
        # 1. 获取资本利得数据 (返回 Series)
        gains_series = yf.Ticker(symbol).get_capital_gains(period=period)

        # 2. 兜底：如果是普通股票或没有派发记录，直接返回空列表
        if gains_series.empty:
            return []

        # 3. 将 Series 转换为 DataFrame，压平日期索引
        df = gains_series.reset_index()

        # 4. 时间格式清洗，转为普通的字符串
        df["Date"] = df["Date"].astype(str)

        # 5. 重命名列名，消除空格，方便你的 Golang 后端定义 struct 字段
        df.rename(columns={"Capital Gains": "CapitalGains"}, inplace=True)

        # 6. 精准达成你的要求：转为字典列表返回
        # 提示：如果 Pylance 还在报红线，可以在这一行最后加上 # type: ignore
        return df.to_dict(orient="records")

    except Exception as e:
        raise ValueError(f"获取 {symbol} 资本利得数据时发生异常: {str(e)}")

def get_shares_full(
    symbol: str, start: str = "", end: str = ""
) -> list[dict]:
    try:
        # 1. 获取历史总股本数据 (返回 Series)
        shares_series = yf.Ticker(symbol).get_shares_full(
            start=start or None,
            end=end or None,
        )

        # 2. 兜底：如果没查到数据，直接返回空列表
        if shares_series is None or shares_series.empty:
            return []

        # 3. 先将 Series 转换为 DataFrame，并指定股本列名为 "Shares"
        # 4. 随后压平日期索引 (Date)
        df = shares_series.to_frame(name="Shares").reset_index()
        df.rename(columns={df.columns[0]: "Date"}, inplace=True)

        # 5. 将时间格式转换为纯字符串 (例如 "2024-05-31")
        df["Date"] = df["Date"].astype(str)

        # 6. 精准达成你的要求：转为字典列表返回
        # 结果长这样: [{"Date": "2024-05-31 00:00:00-04:00", "Shares": 7432309760}, ...]
        return df.to_dict(orient="records")

    except Exception as e:
        raise ValueError(f"获取 {symbol} 历史股本数据时发生异常: {str(e)}")
    
def get_info(symbol: str) -> dict:
    try:
        # 1. 直接获取原生完整的字典数据（包含 150+ 个字段）
        raw_info = yf.Ticker(symbol).get_info()

        # 2. 兜底校验：如果 yfinance 没抓到数据或者股票代码完全不存在
        if not raw_info or "symbol" not in raw_info:
            raise ValueError(f"无法获取股票 {symbol} 的基本面信息，请检查代码是否正确")

        # 3. 完整返回，不作任何精简
        return raw_info

    except ValueError:
        # 放行主动抛出的业务错误
        raise
    except Exception as e:
        # 拦截并包装未知异常（如网络超时、接口变动等）
        raise ValueError(f"请求 {symbol} 基础信息时发生异常: {str(e)}")

def get_fast_info(symbol: str) -> dict:
    try:
        # 1. 直接获取原生完整的极速数据对象
        raw_fast = yf.Ticker(symbol).get_fast_info()

        # 2. 兜底校验：如果 yfinance 没抓到数据或者股票代码完全不存在
        if not raw_fast:
            raise ValueError(
                f"无法获取股票 {symbol} 的极速市场数据，请检查代码是否正确"
            )

        # 3. 完整返回，通过 dict() 转换为标准字典，不作任何精简
        return dict(raw_fast)

    except ValueError:
        # 放行主动抛出的业务错误
        raise
    except Exception as e:
        # 拦截并包装未知异常（如网络超时、接口变动等）
        raise ValueError(f"请求 {symbol} 极速市场数据时发生异常: {str(e)}")

def get_news(symbol: str, count: int = 10, tab: str = "news") -> list[dict]:
    """Allowed options for tab: "news", "all", "press releases"""
    try:
        # 1. 直接获取原生数据
        # 核心注意：它返回的就是 list[dict]，所以不需要 df.to_dict(orient="records")
        raw_news = yf.Ticker(symbol).get_news(count=count, tab=tab)

        # 2. 兜底校验：如果该股票没有任何新闻，返回空列表
        if not raw_news:
            return []

        # 3. 完整返回整个列表，不作任何字段精简
        return raw_news

    except Exception as e:
        # 拦截并包装未知异常
        raise ValueError(f"请求 {symbol} 新闻资讯时发生异常: {str(e)}")

if __name__ == "__main__":
    result = get_news("AAPL")
    print(result)
