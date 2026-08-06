from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.db import get_db
from app.crud.clusters import create_cluster, update_cluster, find_similar_clusters
from app.schemas.clusters import ClusterCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ollama import embedding, generate_cluster
from app.crud.articles import get_article_by_url, create_article
from app.schemas.articles import ArticleCreate
from typing import Annotated
import os

key= os.getenv("N8N_API_KEY")
router = APIRouter(prefix="/n8n")
@router.post("/")
async def ingestion(token: Annotated[str, Header()],article: ArticleCreate, db: AsyncSession = Depends(get_db)):
    if token != key :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token header invalid"
        )
    if await get_article_by_url(db, article.url):
        return 
    embed= await embedding(article.title)
    similar_cluster= await find_similar_clusters(db, embed)
    if (similar_cluster != None):
        article.cluster_id= similar_cluster.id
        article= await create_article(db, article)
        await update_cluster(db, similar_cluster, article)
    else :
        new_cluster= await generate_cluster(article)
        new_cluster= await create_cluster(db, new_cluster)
        article.cluster_id= new_cluster.id
        await create_article(db, article)


