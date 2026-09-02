from typing import Optional
from datetime import datetime,timezone
from fastapi import APIRouter, Depends, HTTPException, Query,Response
from app.db import get_db
from app.crud.clusters import get_clusters, get_cluster_by_id, get_clusters_about_tunisia, get_clusters_by_category
from app.schemas.clusters import ClusterRead, ClusterSummary
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal

router = APIRouter(prefix="/clusters", tags=["clusters"])

@router.get("/", response_model=list[ClusterSummary])
async def list_clusters(response: Response,category: Optional[str] = None, tunisian: bool = False,sort: Literal["latest","top"]= Query(default="top"),
                        window: Literal["24h","7d","30d","all"]= Query(default="7d"),as_of: Optional[datetime] =None, limit: int =Query(default=20, le=50,ge=1),
                        offset: int =Query(default=0 , ge=0),q: Optional[str] = Query(default=None, max_length=120), db: AsyncSession = Depends(get_db)):
    if not as_of:
        as_of=datetime.now(timezone.utc)
    if not as_of.tzinfo:
        as_of=as_of.replace(tzinfo=timezone.utc)
    response.headers["X-as-of"]=as_of.isoformat()
    q = " ".join(q.split()) if q else None   
    if tunisian:
        return await get_clusters_about_tunisia(db,sort,window,as_of,limit,offset,q)
    if category:
        return await get_clusters_by_category(db, category,sort,window,as_of,limit,offset,q)
    return await get_clusters(db,sort,window,as_of,limit,offset,q)

@router.get("/{id}", response_model=ClusterRead)
async def read_cluster(id:int, db: AsyncSession = Depends(get_db)):
    cluster = await get_cluster_by_id(db, id)
    if cluster is None:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster
