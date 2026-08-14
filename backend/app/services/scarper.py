import httpx
from bs4 import BeautifulSoup
import logging
logger = logging.getLogger(__name__)

async def fetch_og_image(url: str):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client :
            response = await client.get(url)
        soup = BeautifulSoup(response.text,  "html.parser")
        tag = soup.find("meta", property="og:image")
        return tag["content"] if tag else None
    except Exception as e:
        logger.error(f"missing data: {e}")
        return None

