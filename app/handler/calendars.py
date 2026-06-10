import pandas as pd
import yfinance as yf


def get_market_calendars(
    start: str | None = None, end: str | None = None
) -> dict[str, list[dict]]:
    try:
        # 1. 初始化日历对象 (不传 start/end 则默认获取今天起未来 7 天)
        cal = yf.Calendars(start=start, end=end)

        # 2. 拉取四大核心日历 (它们原生都是 Pandas DataFrame)
        calendars_map = {
            "earnings": cal.get_earnings_calendar(),
            "ipos": cal.get_ipo_info_calendar(),
            "splits": cal.get_splits_calendar(),
            "economic": cal.get_economic_events_calendar(),
        }

        result: dict[str, list[dict]] = {}

        # 3. 统一遍历、清洗、并全量转换为符合你要求的 list[dict]
        for key, df in calendars_map.items():
            if df is None or df.empty:
                result[key] = []
                continue

            # 压平索引 (日期往往是索引)
            df_flat = df.reset_index()

            # 自动清洗所有 datetime 列，防止 FastAPI 报错
            for col in df_flat.columns:
                if pd.api.types.is_datetime64_any_dtype(df_flat[col]):
                    df_flat[col] = df_flat[col].astype(str)

            # 精准达成你的要求：使用 to_dict(orient="records") 并全量填充
            result[key] = df_flat.to_dict(orient="records")

        return result

    except Exception as e:
        raise ValueError(f"全量获取财经日历数据时发生异常: {str(e)}")

if __name__ == "__main__":
    result = get_market_calendars()
    print(result)