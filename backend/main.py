from fastapi import FastAPI
import db

app = FastAPI()

@app.on_event("startup")
async def startup():
    await db.connect_db()

@app.on_event("shutdown")
async def shutdown():
    await db.close_db()

@app.get("/")
async def root():
    return {"message": "Hello FastAPI"}

@app.get("/health/db")
async def health_db():
    async with db.pool.acquire() as conn:
        result = await conn.fetchval("SELECT 1")
    return {"db": result}
