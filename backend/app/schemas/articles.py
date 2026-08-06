from datetime import datetime

from pydantic import BaseModel, HttpUrl

class ArticleBase(BaseModel):
    title: str
    url: HttpUrl
    source: str
    author: str
    published_at: datetime

class ArticleCreate(ArticleBase):
    pass

class ArticleRead(ArticleBase):
    id: int
    cluster_id: int | None = None
    fetched_at: datetime

    model_config = {"from_attributes": True}
    
