from datetime import datetime
from sqlalchemy import CheckConstraint,  String, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
from pgvector.sqlalchemy import Vector

class Cluster (Base):
    __tablename__= "clusters"

    id: Mapped[int] = mapped_column(primary_key=True)
    main_title: Mapped[str] = mapped_column(String(500))
    latest_published_at: Mapped[datetime] = mapped_column(nullable=True)
    importance_score: Mapped[int] = mapped_column(CheckConstraint("importance_score BETWEEN 0 AND 100"))
    urgency: Mapped[str] = mapped_column(String(10))
    novelty: Mapped[str] = mapped_column(String(10))
    event_type: Mapped[str] = mapped_column()
    one_sentence_summary: Mapped[str] = mapped_column(String(200))
    why_important:  Mapped[str] = mapped_column(String(200))
    recommended_action: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    countries_or_actors: Mapped[list] = mapped_column(ARRAY(String))
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())
    locations: Mapped[list] = mapped_column(ARRAY(String))
    sources: Mapped[list] = mapped_column(ARRAY(String))
    vector = mapped_column(Vector(768))
    articles: Mapped[list["Article"]] = relationship(back_populates="cluster")
