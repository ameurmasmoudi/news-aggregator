from app.models.articles import Article
import httpx

async def embedding(text: str):
    body= {'model': 'nomic-embed-text','input': text}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response= await client.post('http://localhost:11434/api/embed', json=body)
    return response.json()["embeddings"][0]

async def generate_cluster(article: Article):
    body= {'model': 'qwen2.5:7b' ,"stream": False, 'prompt': f"""Return a JSON object. No text before. No text after. No markdown. No backticks. No trailing commas. Only the JSON.

Title: {article.title}
Source: {article.source}

Output must start with {{ and end with }}. Copy this structure exactly, replacing only the values:

{{"main_title":"title here","importance_score":50,"urgency":"medium","novelty":"medium","event_type":"politics","one_sentence_summary":"summary here","why_important":"reason here","recommended_action":"action here","countries_or_actors":["country1"],"locations":["location1"],"category":"politics"}}

Valid urgency values: low, medium, high
Valid novelty values: low, medium, high
Valid event_type values: conflict, politics, economy, technology, environment, health, other
Valid category values: politics, economy, technology, environment, health, conflict, society

JSON:""" 
           }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post('http://localhost:11434/api/generate', json=body)
    return response.json()["response"]
