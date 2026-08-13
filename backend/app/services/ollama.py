from app.models.articles import Article
import httpx

async def embedding(text: str):
    body= {'model': 'nomic-embed-text','input': text}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response= await client.post('http://localhost:11434/api/embed', json=body)
    return response.json()["embeddings"][0]

async def generate_cluster(article: Article):
    body= {'model': 'llama3.2:3b' ,"stream": False ,'prompt':f"""You are a news analyst. Given a news article title,
                                            return ONLY a JSON object with no explanation, no markdown, no backticks.

                                            Article title: {article.title}
                                            Article source: {article.source}

                                            Return this exact JSON structure:   
                                            {{
                                              "main_title": "concise event title",
                                              "importance_score": <0-100>,
                                              "urgency": "low|medium|high",
                                              "novelty": "low|medium|high",
                                              "event_type": "conflict|politics|economy|technology|environment|health|other",
                                              "one_sentence_summary": "one sentence describing the event",
                                              "why_important": "why this event matters",
                                              "recommended_action": "what a reader should do or follow up on",
                                              "countries_or_actors": ["list", "of", "countries", "or", "actors"],
                                              "locations": ["list", "of", "locations"],
                                              "category": "politics|economy|technology|environment|health|conflict|other"
                                            }}"""}
async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post('http://localhost:11434/api/generate', json=body)
    return response.json()["response"]
