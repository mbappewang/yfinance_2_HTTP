import yfinance as yf

# 搜索股票
def search_keyword(keyword,limit=10):
    results = yf.Lookup(keyword).get_all(count=limit)
    return results

def get_stock_info(symbol):
    stock = yf.Ticker(symbol)
    info = stock.get_info()
    return info

# 获取股票历史数据
def get_stock_history(symbol, start_date, end_date):
    stock = yf.Ticker(symbol)
    history = stock.history(start=start_date, end=end_date)
    return history

def get_history_metadata(symbol: str) -> dict:
    try:
        # 【关键修复】：加上括号 ()，让它真正去执行并获取数据
        results = yf.Ticker(symbol).get_history_metadata()

        # 兜底校验（可选）：如果 yfinance 没找到数据返回了空字典
        if not results:
            raise ValueError(f"未找到股票 {symbol} 的历史元数据")

        return results

    except ValueError:
        # 放行主动抛出的业务错误
        raise
    except Exception as e:
        # 包装未知异常
        raise ValueError(f"获取 {symbol} 元数据时发生未知异常: {str(e)}")

if __name__ == "__main__":

    result = yf.Ticker("AAPL").get_dividends(period="max")
    print(result)
    
    