from app.schemas.articles import ArticleCreate
from app.schemas.clusters import ClusterCreate
import pytest_asyncio
import pytest
import os
import logging
from httpx import AsyncClient, ASGITransport
from main import app

logger = logging.getLogger(__name__)

ollama_url=os.getenv("OLLAMA_URL")
key= os.getenv("N8N_API_KEY")
ArticleTest= ArticleCreate(title="test",url="https://www.test.com",source="test",author="test")
ClusterTest= ClusterCreate(main_title="test",urgency="low",category="politics",life_impact="prices",stage="happened",people_affected_stated=0,countries_or_actors=[],one_sentence_summary="this is a test cluster",locations=[])
TestVector= [[0.1]*768]


@pytest.mark.asyncio
async def test_ingestion(httpx_mock):
    header={"token" : key}
    httpx_mock.add_response(
        method="POST",
        url=ollama_url+"/embed",
        json={"embeddings":TestVector},
        status_code=200
        )
    httpx_mock.add_response(
        method="POST",
        url=ollama_url+"/generate",
        json={"response": ClusterTest.model_dump_json()},
        status_code=200
            )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response= await client.post("/n8n/",json=ArticleTest.model_dump(mode="json"),headers=header)
    assert response.status_code == 200
