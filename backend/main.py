from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

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
def get_predict_series(symbol="", start="2024-11-01")

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

