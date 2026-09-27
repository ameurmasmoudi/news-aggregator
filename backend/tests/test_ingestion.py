from app.schemas.articles import ArticleCreate
from app.schemas.clusters import ClusterCreate
import httpx
import pytest_asyncio
import pytest
import os
import logging

logger = logging.getLogger(__name__)

ollama_url=os.getenv("OLLAMA_URL")
key= os.getenv("N8N_API_KEY")
ArticleTest= ArticleCreate(title="test",url="https://www.test.com",source="test",author="test")
ClusterTest= ClusterCreate(main_title="test",life_impact="high",stage="done",people_affected_stated=0,one_sentence_summary="this is a test cluster")
TestVector= [0.1]*768
base= "http://localhost:8000"


@pytest.mark.asyncio
async def test_ingestion(httpx_mock):
    header={"token" : key}
    httpx_mock.add_response(
        method="POST",
        url=ollama_url+"/embed",
        json={"embedding":TestVector},
        status_code=200
        )
    httpx_mock.add_response(
        method="POST",
        url=ollama_url+"/generate",
        json={"response": ClusterTest.model_dump_json()},
        status_code=200
            )
    async with httpx.AsyncClient(timeout=30.0,base_url=base) as client:
        response= await client.post("/n8n/",json=ArticleTest.model_dump(),headers=header)
    assert response.status_code == 200
