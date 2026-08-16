from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from app.db import get_db
from app.crud.clusters import get_clusters, get_cluster_by_id, get_clusters_about_tunisia, get_clusters_by_category
from app.schemas.clusters import ClusterRead, ClusterSummary
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/clusters", tags=["clusters"])

@router.get("/", response_model=list[ClusterSummary])
async def list_clusters(category: Optional[str] = None, tunisian: bool = False, limit: int =Query(default=20, le=50,ge=1),
                        offset: int =Query(default=0 , ge=0), db: AsyncSession = Depends(get_db)):
    if tunisian:
        return await get_clusters_about_tunisia(db,limit,offset)
    if category:
        return await get_clusters_by_category(db, category,limit,offset)
    return await get_clusters(db,limit,offset)

@router.get("/{id}", response_model=ClusterRead)
async def read_cluster(id:int, db: AsyncSession = Depends(get_db)):
    cluster = await get_cluster_by_id(db, id)
    if cluster is None:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster
