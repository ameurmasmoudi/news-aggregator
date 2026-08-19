from datetime import datetime, timezone,timedelta
from typing import Literal
from sqlalchemy.orm import selectinload
from app.models.articles import Article
from app.schemas.clusters import ClusterCreate
from sqlalchemy import String, select, Boolean, any_, or_, case, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.clusters import Cluster
from pgvector.sqlalchemy import Vector
from app.services.scarper import fetch_og_image

async def create_cluster(db: AsyncSession, cluster_to_create: ClusterCreate):
    cluster=Cluster(**cluster_to_create.model_dump())
    db.add(cluster)
    await db.commit()
    await db.refresh(cluster) 
    return cluster

async def get_cluster_by_id(db: AsyncSession, id: int):
    stmt= select(Cluster).where(Cluster.id == id).options(selectinload(Cluster.articles))
    result= await db.scalars(stmt)
    cluster= result.one_or_none()
    return cluster

async def get_clusters(db: AsyncSession,sort: Literal["latest","top"],window: Literal["24h","7d","30d","all"],as_of: datetime,limit: int,offset:int):
    stmt= select(Cluster).options(selectinload(Cluster.articles))
    stmt = apply_feed(stmt,sort,window,as_of,limit,offset)
    result= await db.execute(stmt)
    clusters= []
    for cluster,score in result.all():
        cluster.score= score
        clusters.append(cluster)
    return clusters


async def update_cluster(db: AsyncSession, cluster_to_update: Cluster, article: Article):
    cluster= await db.get(Cluster,cluster_to_update.id)
    cluster.latest_published_at= article.published_at
    cluster.updated_at= datetime.now(timezone.utc)
    if not (article.source in cluster.sources):
        cluster.sources.append(article.source)
    cluster.articles.append(article)
    if not cluster.image :
        if not article.image_url :
            article.image_url = await fetch_og_image(str(article.url))
        cluster.image = article.image_url    
    await db.commit()
    await db.refresh(cluster)
    return cluster

async def find_similar_clusters(db: AsyncSession, vect: Vector):
    cosine_similarity = (1 - Cluster.vector.cosine_distance(vect))
    stmt = select(Cluster).where(cosine_similarity > 0.85).order_by(cosine_similarity.desc()).limit(1)
    result= await db.scalars(stmt)
    cluster=result.one_or_none()
    if cluster :
        return cluster
    return None

async def get_clusters_by_category(db: AsyncSession, category: str,sort: Literal["latest","top"],window: Literal["24h","7d","30d","all"],as_of: datetime,limit:int,offset:int):
    stmt = select(Cluster).where(Cluster.category == category).options(selectinload(Cluster.articles))
    stmt = apply_feed(stmt,sort,window,as_of,limit,offset)
    result= await db.execute(stmt)
    clusters= []
    for cluster,score in result.all():
        cluster.score= score
        clusters.append(cluster)
    return clusters


async def get_clusters_about_tunisia(db: AsyncSession,sort: Literal["latest","top"],window: Literal["24h","7d","30d","all"],as_of:datetime,limit:int,offset:int):
    stmt = select(Cluster).where(or_(Cluster.sources.overlap(["kapitalis" , "nawaat"]), any_(Cluster.locations) =="Tunisia", any_(Cluster.countries_or_actors)=="Tunisia")).options(selectinload(Cluster.articles))
    stmt = apply_feed(stmt,sort,window,as_of,limit,offset)
    result= await db.execute(stmt)
    clusters= []
    for cluster,score in result.all():
        cluster.score= score
        clusters.append(cluster)
    return clusters

def score_expr(as_of:datetime):
    urgency = case((Cluster.urgency == "high",1),(Cluster.urgency == "medium",0.5), else_ = 0.0)
    novelty = case((Cluster.novelty == "high",1),(Cluster.novelty == "medium",0.5), else_ = 0.0)
    coverage = func.least(func.cardinality(Cluster.sources),6)/6.0
    age_hours = func.greatest(func.extract("epoch", as_of - Cluster.latest_published_at),0)/3600.0
    decay = case((Cluster.latest_published_at.is_(None),0.0),else_ =func.power(0.5, age_hours / 48.0))
    base = (Cluster.importance_score / 100)*0.4 + urgency *0.25 + novelty *0.15 + coverage *0.2
    return (base * decay).label("score")

window_dict={"24h":timedelta(hours=24),"7d":timedelta(days=7),"30d":timedelta(days=30)}
def apply_feed(stmt:select,sort: Literal["latest","top"],window: Literal["24h","7d","30d","all"],as_of: datetime,limit:int,offset:int):
    score=score_expr(as_of)
    stmt= stmt.add_columns(score)
    if window in {"24h","7d","30d"}:
        delta= window_dict[window]
        stmt = stmt.where(Cluster.latest_published_at>(as_of - delta))
    if sort=="latest":
        stmt= stmt.order_by(Cluster.latest_published_at.desc().nulls_last())
    else:
        stmt= stmt.order_by(score.desc()).order_by(Cluster.id.desc())
    stmt= stmt.limit(limit).offset(offset)
    return(stmt)
