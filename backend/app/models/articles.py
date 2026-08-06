from datetime import datetime
from sqlalchemy import String, func, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class Article(Base):
    __tablename__ = "articles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("clusters.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(2048), unique=True)
    source: Mapped[str] = mapped_column(String(100))
    author: Mapped[str] = mapped_column(String(100), nullable=True)
    published_at: Mapped[datetime] = mapped_column(nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(server_default=func.now())
    cluster: Mapped["Cluster"] = relationship(back_populates="articles")
