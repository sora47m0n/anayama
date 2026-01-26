from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from supabase import create_client, Client
from datetime import datetime


# 受付窓口
app = FastAPI()

#フロントからのアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # --- 設定 --
SUPABASE_URL = "https://ogjpslisorqbztlzhocd.supabase.co"
# # ★ここに ey から始まる Service Role Key (管理者キー) を貼り付けてください★
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9nanBzbGlzb3JxYnp0bHpob2NkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODkyOTQzMiwiZXhwIjoyMDg0NTA1NDMyfQ.pfZdwXZfjYMQcmlYQHahp-x6TP5v37V157X859hzneg" 
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

#日付を変換する関数
def mmdd(date_str: str) -> str:
    d = datetime.fromisoformat(date_str[:10])
    return f"{d.month}/{d.day}"


# 返すデータの型
class Row(BaseModel):
    date: str
    actual: Optional[float] = None
    pred: Optional[float] = None

# 初期表示
@app.get("/")
async def root():
    return {"message": "Hello FastAPI"}

#DBから実値、予測値をフロントに返す
#(response_modelはreturnで返す型を表す)
@app.get("/api/predict-series", response_model=List[Row])
def get_predict_series(
    symbol="", 
    actual_start="2025-11-20",
    actual_end="2025-11-28",
    pred_start="2025-12-01",
    pred_end="2025-12-01"
):
    # market_pricesから実測を取得
    actual_res = (
        supabase.table("market_prices")
        .select("trade_date, close_price")
        .eq("symbol", symbol)
        .gte("trade_date", actual_start)
        .lte("trade_date", actual_end)
        .order("trade_date")
        .execute()
    )

    if getattr(actual_res, "error", None):
        return [{"date": "", "actual": None, "pred": None}]

    # prediction_resultsから予測＋実測を取得
    pred_res = (
        supabase.table("prediction_results")
        .select("target_date, predicted_close, actual_close")
        .eq("stock_code", symbol)
        .gte("target_date", pred_start)
        .lte("target_date", pred_end)
        .order("target_date")
        .execute()
    )

    if getattr(pred_res, "error", None):
        return [{"date": "", "actual": None, "pred": None}]

    # 返す箱
    merged: Dict[str,dict] = {}

    # 実測を入れる
    for i in (actual_res.data or []):
        d_iso = i["trade_date"][:10] #yyyy-mm-dd
        # 同じ日付があったら作成
        merged.setdefault(d_iso,{"date":mmdd(d_iso),"actual":None,"pred":None})

        close_price = i.get("close_price")

        merged[d_iso]["actual"] = float(close_price) if close_price is not None else None

    # 予測を入れる
    for i in (pred_res.data or []):
        d_iso = i["target_date"][:10]
        merged.setdefault(d_iso,{"date":mmdd(d_iso), "actual":None, "pred":None})
        
        predicted = i.get("predicted_close")
        merged[d_iso]["pred"] = float(predicted) if predicted is not None else None

        actual_close = i.get("actual_close")
        merged[d_iso]["actual"] = float(actual_close) if actual_close is not None else None
    
    result = [merged[d] for d in sorted(merged.keys())]
    return result


# @app.get("/api/predict-series", response_model=List[Row])
# async def predict_output():

#     return [
#         { "date": "12/1", "actual": 900,  "pred": 880 },
#         { "date": "12/2", "actual": 820,  "pred": 840 },
#         { "date": "12/3", "actual": 950,  "pred": 910 },
#         { "date": "12/4", "actual": 1000, "pred": 930 },
#         { "date": "12/5", "actual": None, "pred": 930 },
#         { "date": "12/6", "actual": None, "pred": 1000 }
#     ]

