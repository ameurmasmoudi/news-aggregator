from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os
from sqlalchemy.orm import DeclarativeBase
load_dotenv()
DATABASE_URL= os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

url = make_url(DATABASE_URL).set(drivername="postgresql+asyncpg")
sslmode = url.query.get("sslmode")
url = url.difference_update_query(["sslmode", "channel_binding"])
connect_args = {"ssl": "require"} if sslmode and sslmode != "disable" else {}
if "-pooler." in (url.host or ""):
    connect_args["statement_cache_size"] = 0

engine = create_async_engine(url, echo=False, poolclass=NullPool, connect_args=connect_args)
SessionLocal = async_sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as db:
        yield db

