import logging 
from app.services.scarper import fetch_og_image
from fastapi import APIRouter, Depends, Header, status, HTTPException
from app.db import get_db
from app.crud.clusters import create_cluster, update_cluster, find_similar_clusters
from app.schemas.clusters import ClusterCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ollama import embedding, generate_cluster
from app.crud.articles import get_article_by_url, create_article
from app.schemas.articles import ArticleCreate
from typing import Annotated
import os
import json
logger = logging.getLogger(__name__)

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
    try:
        embed= await embedding(article.title)
    except Exception as e:
        logger.error(f"embedding failed for article: {article.title}: {e}")
        return
    similar_cluster= await find_similar_clusters(db, embed)
    if (similar_cluster != None):
        article.cluster_id= similar_cluster.id
        article= await create_article(db, article)
        await update_cluster(db, similar_cluster, article)
    else :
        try:
            new_cluster_raw = await generate_cluster(article)
            cluster_data = json.loads(new_cluster_raw)
        except Exception as e:
            logger.error(f"LLM returned invalid JSON: {e}")
            return
        cluster_data["embedding"] = embed
        if not article.image_url:
            article.image_url = await fetch_og_image(str(article.url))
        cluster_data["image"]=article.image_url
        cluster_data["latest_published_at"]=article.published_at
        cluster_data["sources"]=[article.source]
        try:
            new_cluster = ClusterCreate(**cluster_data)
        except Exception as e:
            logger.error(f"missing data: {e}")
            return
        new_cluster = await create_cluster(db, new_cluster)
        article.cluster_id= new_cluster.id
        await create_article(db, article)


