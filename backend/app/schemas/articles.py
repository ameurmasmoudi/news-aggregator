from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl

class ArticleBase(BaseModel):
    title: str
    url: HttpUrl
    source: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None 

class ArticleCreate(ArticleBase):
    cluster_id: Optional[int] = None
    image_url: Optional[str] = None
    pass

class ArticleRead(ArticleBase):
    id: int
    cluster_id: int | None = None
    fetched_at: datetime

    model_config = {"from_attributes": True}
    
