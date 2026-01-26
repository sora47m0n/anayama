from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
# from supabase_client import get
import db,os
import asyncpg
import ssl


# DB住所定義
# DATABASE_URL = os.environ["DATABASE_URL"]
DATABASE_URL = "postgresql://postgres.ogjpslisorqbztlzhocd:fbifaufiuaef@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

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

# 返すデータの型
class Row(BaseModel):
    date: str
    actual: Optional[float] = None
    pred: Optional[float] = None

# プールの作成（接続を使いまわしできるイメージ）
pool: asyncpg.Pool | None = None

# 初期表示
@app.get("/")
async def root():
    return {"message": "Hello FastAPI"}

# 起動時のプール作成
@app.on_event("startup")
async def startup():
    global pool
    #暗号化ルールの設定
    ssl_ctx = ssl.create_default_context()
    #プールの作成
    # pool = await asyncpg.create_pool(DATABASE_URL, ssl=ssl_ctx, min_size=1, max_size=5)

@app.on_event("shutdown")
async def shutdown():
    await pool.close()

@app.get("/health")
async def health_db():
    if pool is None:
        raise HTTPException(status_code=500,detail="DB pool is not initialized")
    
    async with pool.acquire() as conn:
        v = await conn.fetchval("select 1;")
    return {"db": v}

@app.get("/api/predict-series", response_model=List[Row])
async def predict_output():

    return [
        { "date": "12/1", "actual": 900,  "pred": 880 },
        { "date": "12/2", "actual": 820,  "pred": 840 },
        { "date": "12/3", "actual": 950,  "pred": 910 },
        { "date": "12/4", "actual": 1000, "pred": 930 },
        { "date": "12/5", "actual": None, "pred": 930 },
        { "date": "12/6", "actual": None, "pred": 1000 }
    ]

# @app.get("/api/predict-series", resuponse_model=List[Row])
# async def get_predict_series():
# """
#     返す形：[{date, actual, pred}, ...]
#     - 11月：actualだけ
#     - 12/1：predだけ
#     みたいな穴あきでも返せるように FULL OUTER JOIN を使う例
# """
#     assert pool is not None

#     sql = """
#     SELECT
#         to_char(coalesce(t.trade_date,p.target_date), 'MM/DD') as date,
#         t.close_price as actual,
#         p.predicted_close as pred
#     FROM market_prices t

