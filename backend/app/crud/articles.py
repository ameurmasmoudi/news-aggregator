from app.models import articles
from app.schemas.articles import ArticleCreate
from sqlalchemy import select
from pydantic import HttpUrl
from app.models.articles import Article
from sqlalchemy.ext.asyncio import AsyncSession

async def get_article_by_url(db: AsyncSession, url: HttpUrl):
    stmt = select(Article).where(Article.url == url)
    response = await db.scalars(stmt)
    article = response.one_or_none()
    return article

async def create_article(db: AsyncSession, article_to_add: ArticleCreate):
    article = Article(**article_to_add.model_dump())
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article


async def get_article_by_id(db: AsyncSession, id: int):
    stmt = select(Article).where(Article.id == id)
    response = db.scalars(stmt)
    article = response.one_or_none()
    return article


async def get_articles(db: AsyncSession):
    stmt = select(Article)
    response = await db.scalars(stmt)
    articles = response.all()
    return articles


