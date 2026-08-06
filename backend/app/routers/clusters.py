from fastapi import APIRouter, Depends, HTTPException
from app.db import get_db
from app.crud.clusters import get_clusters, get_cluster_by_id
from app.schemas.clusters import ClusterRead
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/clusters", tags=["clusters"])

@router.get("/", response_model=list[ClusterRead])
async def read_clusters(db: AsyncSession = Depends(get_db)):
    return await get_clusters(db)

@router.get("/{id}", response_model=ClusterRead)
async def read_cluster(id:int, db: AsyncSession = Depends(get_db)):
    cluster = await get_cluster_by_id(db, id)
    if cluster is None:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster
