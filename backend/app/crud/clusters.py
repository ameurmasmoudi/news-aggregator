from datetime import datetime, timezone

from app.models.articles import Article
from app.schemas.clusters import ClusterCreate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.clusters import Cluster
from pgvector.sqlalchemy import Vector

async def create_cluster(db: AsyncSession, cluster_to_create: ClusterCreate):
    cluster=Cluster(**cluster_to_create.model_dump())
    db.add(cluster)
    await db.commit()
    await db.refresh(cluster)
    return cluster

async def get_cluster_by_id(db: AsyncSession, id: int):
    stmt= select(Cluster).where(Cluster.id == id)
    result= await db.scalars(stmt)
    cluster= result.one_or_none()
    return cluster

async def get_clusters(db: AsyncSession):
    stmt= select(Cluster)
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

