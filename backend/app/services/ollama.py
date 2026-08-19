from app.models.articles import Article
import httpx

CLUSTER_SCHEMA = {
    "type": "object",
    "properties": {
        "main_title":          {"type": "string"},
        "one_sentence_summary": {"type": "string"},
        "importance_score":    {"type": "integer", "minimum": 0, "maximum": 100},
        "urgency":             {"type": "string", "enum": ["low", "medium", "high"]},
        "novelty":             {"type": "string", "enum": ["low", "medium", "high"]},
        "countries_or_actors": {"type": "array", "items": {"type": "string"}},
        "locations":           {"type": "array", "items": {"type": "string"}},
        "category": {"type": "string", "enum": [
            "politics", "economy", "technology", "science",
            "environment", "health", "conflict", "society",
        ]},
    },
    "required": [
        "main_title", "one_sentence_summary","importance_score", "urgency", "novelty",
        "countries_or_actors", "locations", "category",
    ],
}

SYSTEM = """You are a wire-desk editor triaging incoming headlines for an international news feed.
You judge each story's weight the way a duty editor does: quickly, comparatively, and without
inflating routine copy. You never invent facts that are not in the headline you are given."""

PROMPT = """Headline: {title}
Outlet: {source}

FIELDS
  main_title            A clean neutral rewrite of the headline. Strip the outlet name, ALL CAPS,
                        emoji, and clickbait framing ("You won't believe...", "Here's why...").
                        Keep it under 120 characters.
  one_sentence_summary  One sentence saying what happened, who is involved, and where. It must add
                        something beyond restating main_title. If the headline is too vague to say
                        more, stay vague — do not guess details.
  countries_or_actors   Named states, organisations, companies or people driving the story.
                        Empty list if the headline names none. Do not infer.
  locations             Where the event happens. Use "global" only when it genuinely has no
                        geographic centre. Empty list if unknown.
  category              Exactly one from the schema enum.


Score this story.

IMPORTANCE (0-100) — how much it matters to a well-informed international reader.
  90-100  Global rupture: war between major powers, death or removal of a head of state,
          financial system crisis, mass-casualty catastrophe.
  70-89   Major event: national election result, large attack or disaster, central bank rate
          decision, war escalation, major legal ruling against a state or global company.
  50-69   Significant but bounded: notable legislation, regional unrest, large corporate
          collapse or merger, a scientific result with real-world consequences.
  30-49   News of record: routine politics, quarterly earnings, a local crime, a policy
          proposal, a sports result of wide interest.
  10-29   Soft copy: lifestyle, listicles, reviews, opinion, human interest, product news.
  0-9     Trivia: celebrity gossip, promotional content, horoscopes.

  Most RSS headlines belong in 20-45. Use the full range. If you are about to answer 50,
  you have not decided yet — re-read the bands and commit to one.

URGENCY — how fast this matters.
  high    Unfolding now, a reader may need to know within hours: ongoing attack, evacuation,
          market halt, breaking casualty report, imminent deadline.
  medium  Developing over days: a decision just taken, a trial under way, a storm approaching.
  low     Not time-bound: analysis, feature, retrospective, review, profile.

NOVELTY — how new this is.
  high    First report of a development that was not known yesterday.
  medium  A new turn in a story already running.
  low     Recap, explainer, opinion or analysis of facts already reported.
EXAMPLES

Headline: "Russian strike on Kharkiv apartment block kills 14, regional governor says"
{{"main_title":"Russian strike on Kharkiv apartment block kills 14","one_sentence_summary":"A Russian missile hit a residential
building in Kharkiv, killing at least 14 people according to the regional governor.",
"importance_score":84,"urgency":"high","novelty":"high",
"countries_or_actors":["Russia","Ukraine"],"locations":["Kharkiv","Ukraine"],"category":"conflict"}}

Headline: "Dickovers, baggravation and botiquette: 18 new words to describe our tech hellscape"
{{"main_title":"Eighteen new words coined to describe modern technology frustrations","one_sentence_summary":"A feature
proposes eighteen new terms for common irritations of everyday technology use.",
"importance_score":12,"urgency":"low","novelty":"medium",
"countries_or_actors":[],"locations":[],"category":"society"}}

Headline: "Tunisian parliament passes 2027 budget after three days of debate"
{{"main_title":"Tunisian parliament passes 2027 budget","one_sentence_summary":"Tunisia's parliament approved the 2027 budget following
three days of debate.","importance_score":41,"urgency":"medium",
"novelty":"high","countries_or_actors":["Tunisia"],"locations":["Tunisia"],
"category":"economy"}}

Now score the headline above."""
 
async def embedding(text: str):
    body= {'model': 'nomic-embed-text','input': text}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response= await client.post('http://localhost:11434/api/embed', json=body)
    return response.json()["embeddings"][0]

async def generate_cluster(article: Article):
   
    body= {'model': 'qwen2.5:7b' ,"stream": False,"system": SYSTEM,"prompt": PROMPT.format(title=article.title,source=article.source),"format": CLUSTER_SCHEMA,"options": {"temperature":0,"num_predict": 400}         }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post('http://localhost:11434/api/generate', json=body)
    return response.json()["response"]
