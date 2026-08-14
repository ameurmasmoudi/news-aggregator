from datetime import datetime
from app.schemas.articles import ArticleRead
from pydantic import BaseModel, HttpUrl

class ClusterBase(BaseModel):
    main_title: str
    importance_score: int
    urgency: str
    novelty: str
    event_type: str
    one_sentence_summary: str | None
    why_important: str
    recommended_action: str | None
    countries_or_actors: list[str] = []
    locations: list[str] = []
    sources: list[str] = []
    category: str | None = None
    image: str | None = None

class ClusterCreate(ClusterBase):
    pass

class ClusterRead(ClusterBase):
    id: int
    latest_published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    articles: list[ArticleRead]= []

    model_config = {"from_attributes": True}

