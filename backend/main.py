from app.routers import articles, clusters, ingestion
from fastapi import FastAPI, Depends
from app.db import get_db
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()
app.include_router(articles.router)
app.include_router(clusters.router)
app.include_router(ingestion.router)

@app.get("/health")
async def health(db : AsyncSession = Depends(get_db)):
    await db.execute(text("select 1"))
    return {"status": "ok"}
