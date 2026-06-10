import yfinance as yf
import pandas as pd
import math

def lookup(
    query: str,
    type: str = "all",
    count: int = 25,
    timeout: int = 30,
) -> list[dict]:
    try:
        lookup_obj = yf.Lookup(query, timeout=timeout)

        method_map = {
            "all": lookup_obj.get_all,
            "stock": lookup_obj.get_stock,
            "etf": lookup_obj.get_etf,
            "cryptocurrency": lookup_obj.get_cryptocurrency,
            "currency": lookup_obj.get_currency,
            "future": lookup_obj.get_future,
            "index": lookup_obj.get_index,
            "mutualfund": lookup_obj.get_mutualfund,
        }

        if type not in method_map:
            raise ValueError(
                f"不支持的模糊查找类型: {type}。可选范围: {list(method_map.keys())}"
            )

        df: pd.DataFrame = method_map[type](count=count)

        if df is None or df.empty:
            return []

        # 1. 压平索引
        df = df.reset_index()

        # 2. 转换时间类型为字符串
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)

        # 3. 获取原生字典列表（此时里面还藏着 Pandas 甩不掉的 nan）
        raw_records = df.to_dict(orient="records")

        # ✨ 4. 【终极清洗】：纯 Python 暴力排雷，百分百消灭 nan
        cleaned_records = []
        for row in raw_records:
            cleaned_row = {}
            for key, value in row.items():
                # 判断是不是烦人的 nan (只有 float 类型的 nan 会出现不等于自身的情况，或者用 math.isnan)
                if isinstance(value, float) and math.isnan(value):
                    cleaned_row[key] = (
                        None  # 强行转为标准的 Python None (JSON 中的 null)
                    )
                else:
                    cleaned_row[key] = value
            cleaned_records.append(cleaned_row)

        return cleaned_records

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"通过关键字 '{query}' 查找资产时发生未知异常: {str(e)}")
    
if __name__ == "__main__":
    result = lookup("QQQ","all",1)
    print(result)