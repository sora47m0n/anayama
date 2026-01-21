from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import db,os
import asyncpg

# DB住所定義
DATABASE_URL = os.environ["DATABASE_URL"]

# 受付窓口
app = FastAPI()

#フロントからのアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"]
)

# 返すデータの型
class Row(BaseModel):
    date: star
    actual: Optional[float] = None
    pred: Optional[float] = None

# プールの作成（接続を使いまわしできるイメージ）
pool: asyncpg.Pool | None = None

# 初期表示
@app.get("/")
async def root():
    return {"message": "Hello FastAPI"}

@app.on_event("startup")
async def startup():
    global pool
    #暗号化ルールの設定
    ssl_ctx = ssl.create_default_context()
    #プールの作成
    pool = await asyncpg.create_pool(DATABASE_URL, ssl=ssl_ctx)

@app.on_event("shutdown")
async def shutdown():
    await pool.close()

@app.get("/health")
async def health_db():
    return {"db": result}

@app.get("/predict")
async def predict_output():
    return "aaaa"

# @app.get("/api/predict-series", resuponse_model=List[Row])
# async def get_predict_series(symbol: str = "SPY"):
# """
#     返す形：[{date, actual, pred}, ...]
#     - 11月：actualだけ
#     - 12/1：predだけ
#     みたいな穴あきでも返せるように FULL OUTER JOIN を使う例
#     """
#     assert pool is not None

#     # ✅ あなたの実テーブル名/カラム名に合わせて変更してOK
#     sql = """
#     SELECT
#       to_char(coalesce(t.date, p.date), 'MM/DD') AS date,
#       t.actual AS actual,
#       p.pred AS pred
#     FROM training_data t
#     FULL OUTER JOIN predictions p
#       ON t.symbol = p.symbol
#      AND t.date   = p.date
#     WHERE coalesce(t.symbol, p.symbol) = $1
#     ORDER BY coalesce(t.date, p.date);
#     """

#     rows = await pool.fetch(sql, symbol)
#     return [dict(r) for r in rows]
