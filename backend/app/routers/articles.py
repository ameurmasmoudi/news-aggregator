from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.crud.articles import get_articles, get_article_by_id
from app.schemas.articles import ArticleRead

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/", response_model=list[ArticleRead])
async def read_articles(db: AsyncSession = Depends(get_db)):
    return await get_articles(db)

@router.get("/{id}", response_model=ArticleRead)
async def read_article(id: int, db: AsyncSession = Depends(get_db)):
    article = await get_article_by_id(db, id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
