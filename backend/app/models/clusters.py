from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime,  String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
from pgvector.sqlalchemy import Vector

class Cluster (Base):
    __tablename__= "clusters"

    id: Mapped[int] = mapped_column(primary_key=True)
    main_title: Mapped[str] = mapped_column(String(500))
    latest_published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=True)
    life_impact: Mapped[str] =  mapped_column(String(20), nullable=True)
    urgency: Mapped[str] = mapped_column(String(10))
    one_sentence_summary: Mapped[str] = mapped_column(Text(), nullable=True)
    stage: Mapped[str] = mapped_column(String(20), nullable=True)
    people_affected_stated: Mapped[int] = mapped_column(server_default="0", default=0)
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    countries_or_actors: Mapped[list] = mapped_column(ARRAY(String))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    locations: Mapped[list] = mapped_column(ARRAY(String))
    sources: Mapped[list] = mapped_column(ARRAY(String))
    vector = mapped_column(Vector(768))
    articles: Mapped[list["Article"]] = relationship(back_populates="cluster")
    image: Mapped[str] = mapped_column(String(2048), nullable=True)

    @property
    def article_count(self) -> int :
        return len(self.articles)
