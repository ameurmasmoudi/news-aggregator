from datetime import datetime, timezone
from sqlalchemy.orm import selectinload
from app.models.articles import Article
from app.schemas.clusters import ClusterCreate
from sqlalchemy import String, select, Boolean, any_, or_
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

async def get_clusters(db: AsyncSession,limit: int,offset:int):
    stmt= select(Cluster).options(selectinload(Cluster.articles)).order_by(Cluster.latest_published_at.desc().nulls_last()).limit(limit).offset(offset)
    result= await db.scalars(stmt)
    clusters= result.all()
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

async def get_clusters_by_category(db: AsyncSession, category: str,limit:int,offset:int):
    stmt = select(Cluster).where(Cluster.category == category).options(selectinload(Cluster.articles)).order_by(Cluster.latest_published_at.desc().nulls_last()).limit(limit).offset(offset)
    result= await db.scalars(stmt)
    clusters= result.all()
    return clusters

async def get_clusters_about_tunisia(db: AsyncSession,limit:int,offset:int):
    stmt = select(Cluster).where(or_(Cluster.sources.overlap(["kapitalis" , "nawaat"]), any_(Cluster.locations) =="Tunisia", any_(Cluster.countries_or_actors)=="Tunisia")).options(selectinload(Cluster.articles)).order_by(Cluster.latest_published_at.desc().nulls_last()).limit(limit).offset(offset)
    result= await db.scalars(stmt)
    clusters= result.all()
    return clusters
