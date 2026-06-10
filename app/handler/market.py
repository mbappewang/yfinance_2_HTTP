import yfinance as yf


def market(market_name: str) -> dict:
    """
    获取指定交易市场的全量宏观数据
    """
    try:
        # 1. 初始化市场对象
        m = yf.Market(market_name)

        # 2. 全量拉取两个核心属性
        raw_status = m.status
        raw_summary = m.summary

        # 3. 【核心修复】使用 getattr 安全且动态地获取 to_dict 方法
        # 如果 raw_summary 是 DataFrame，to_dict_method 会拿到对应的函数，否则拿到 None
        to_dict_method = getattr(raw_summary, "to_dict", None)

        if to_dict_method and callable(to_dict_method):
            # 如果存在 to_dict 方法（说明是 DataFrame），执行转换
            processed_summary = to_dict_method(orient="records")
        else:
            # 如果是原生的 dict，或者为 None，则直接透传（若为 None 则降级为空列表）
            processed_summary = raw_summary if raw_summary is not None else []

        # 4. 保持统一队形，全量返回
        return {
            "market": market_name,
            "status": raw_status,
            "summary": processed_summary,
        }

    except Exception as e:
        raise ValueError(f"请求 {market_name} 市场宏观数据时发生异常: {str(e)}")
