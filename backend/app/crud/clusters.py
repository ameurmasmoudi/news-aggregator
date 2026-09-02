from datetime import datetime, timezone,timedelta
from typing import Literal
from sqlalchemy.orm import selectinload
from app.models.articles import Article
from app.schemas.clusters import ClusterCreate
from sqlalchemy import String, select, Boolean, any_, or_, and_, case, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.clusters import Cluster
from pgvector.sqlalchemy import Vector
from app.services.scarper import fetch_og_image
from app.config import ranking as cfg

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

async def get_clusters(db: AsyncSession,sort: Literal["latest","top"],window: Literal["24h","7d","30d","all"],as_of: datetime,limit: int,offset:int,q:str |None = None):
    stmt= select(Cluster).options(selectinload(Cluster.articles))
    stmt = apply_feed(stmt,sort,window,as_of,limit,offset,q)
    result= await db.execute(stmt)
    clusters= []
    for cluster,score in result.all():
        cluster.score= score
        clusters.append(cluster)
    return clusters


async def update_cluster(db: AsyncSession, cluster_to_update: Cluster, article: Article):
    cluster= await db.get(Cluster,cluster_to_update.id)
    if (article.published_at is not None) and (cluster.latest_published_at is None or article.published_at > cluster.latest_published_at):
        cluster.latest_published_at = article.published_at
    cluster.updated_at= datetime.now(timezone.utc)
    if not (article.source in cluster.sources):
        cluster.sources= cluster.sources + [article.source]
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
    stmt = select(Cluster).where(cosine_similarity > 0.85,Cluster.latest_published_at > datetime.now(timezone.utc) - timedelta(days=7)).order_by(cosine_similarity.desc()).limit(1)
    result= await db.scalars(stmt)
    cluster=result.one_or_none()
    if cluster :
        return cluster
    return None

async def get_clusters_by_category(db: AsyncSession, category: str,sort: Literal["latest","top"],window: Literal["24h","7d","30d","all"],as_of: datetime,limit:int,offset:int,q:str |None = None):
    stmt = select(Cluster).where(Cluster.category == category).options(selectinload(Cluster.articles))
    stmt = apply_feed(stmt,sort,window,as_of,limit,offset,q)
    result= await db.execute(stmt)
    clusters= []
    for cluster,score in result.all():
        cluster.score= score
        clusters.append(cluster)
    return clusters


async def get_clusters_about_tunisia(db: AsyncSession,sort: Literal["latest","top"],window: Literal["24h","7d","30d","all"],as_of:datetime,limit:int,offset:int,q:str |None = None):
    stmt = select(Cluster).where(or_(Cluster.sources.overlap(["kapitalis" , "nawaat"]), any_(Cluster.locations) =="Tunisia", any_(Cluster.countries_or_actors)=="Tunisia")).options(selectinload(Cluster.articles))
    stmt = apply_feed(stmt,sort,window,as_of,limit,offset,q)
    result= await db.execute(stmt)
    clusters= []
    for cluster,score in result.all():
        cluster.score= score
        clusters.append(cluster)
    return clusters

def weight_map(col, mapping, default):
    return case(*[(col == k, float(v)) for k, v in mapping.items()], else_=default)

def score_expr(as_of: datetime):
    topic   = weight_map(Cluster.category,    cfg.TOPIC_WEIGHT,   1.0)
    impact  = weight_map(Cluster.life_impact, cfg.IMPACT_WEIGHT,  0.5)
    stage   = weight_map(Cluster.stage,       cfg.STAGE_WEIGHT,   0.5)
    urgency = weight_map(Cluster.urgency,     cfg.URGENCY_WEIGHT, 0.5)

    coverage = func.least(func.cardinality(Cluster.sources), cfg.COVERAGE_CAP) / float(cfg.COVERAGE_CAP)

    toll = func.least(func.log(Cluster.people_affected_stated + 1) / cfg.TOLL_LOG_DIVISOR, 1.0)

    story_age_hours = func.extract("epoch", as_of - Cluster.created_at) / 3600.0
    novelty = func.power(0.5, func.least(story_age_hours / cfg.STORY_HALF_LIFE_HOURS,700.0))

    w = cfg.PART_WEIGHT
    substance = (w["impact"]   * impact
               + w["coverage"] * coverage
               + w["stage"]    * stage
               + w["toll"]     * toll
               + w["urgency"]  * urgency
               + w["novelty"]  * novelty)

    age_hours = func.greatest(func.extract("epoch", as_of - Cluster.latest_published_at), 0) / 3600.0
    decay = case((Cluster.latest_published_at.is_(None), 0.0),
                 else_=func.power(0.5, func.least(age_hours / cfg.HALF_LIFE_HOURS,700.0)))

    return (topic * substance * decay).label("score")

window_dict={"24h":timedelta(hours=24),"7d":timedelta(days=7),"30d":timedelta(days=30)}
def apply_feed(stmt:select,sort: Literal["latest","top"],window: Literal["24h","7d","30d","all"],as_of: datetime,limit:int,offset:int,q:str | None = None):
    score=score_expr(as_of)
    stmt= stmt.add_columns(score)
    if q:
        stmt = stmt.where(_like_filter(q))
    if window in {"24h","7d","30d"}:
        delta= window_dict[window]
        stmt = stmt.where(Cluster.latest_published_at>(as_of - delta))
    if sort=="latest":
        stmt= stmt.order_by(Cluster.latest_published_at.desc().nulls_last())
    else:
        stmt= stmt.order_by(score.desc()).order_by(Cluster.id.desc())
    stmt= stmt.limit(limit).offset(offset)
    return(stmt)

def _like_filter(q: str):
    clauses = []
    for token in q.split():
        safe = token.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{safe}%"
        clauses.append(or_(
            Cluster.main_title.ilike(pattern, escape="\\"),
            Cluster.one_sentence_summary.ilike(pattern, escape="\\"),
        ))
    return and_(*clauses)


