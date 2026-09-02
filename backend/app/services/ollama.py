from app.models.articles import Article
import httpx

CLUSTER_SCHEMA = {
    "type": "object",
    "properties": {
        "main_title":             {"type": "string"},
        "one_sentence_summary":   {"type": "string"},
        "category": {"type": "string", "enum": [
            "politics", "economy", "technology", "science",
            "environment", "health", "conflict", "society"]},
        "life_impact": {"type": "string", "enum": [
            "prices", "work", "movement", "safety", "services", "rights", "none"]},
        "stage": {"type": "string", "enum": [
            "happened", "decided", "proposed", "discussed"]},
        "people_affected_stated": {"type": "integer", "minimum": 0},
        "urgency":                {"type": "string", "enum": ["low", "medium", "high"]},
        "countries_or_actors":    {"type": "array", "items": {"type": "string"}},
        "locations":              {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "main_title", "one_sentence_summary", "category", "life_impact", "stage",
        "people_affected_stated", "urgency", "countries_or_actors", "locations",
    ],
}

SYSTEM = """You are a wire-desk editor triaging incoming headlines for an international news feed.
You judge each story's weight the way a duty editor does: quickly, comparatively, and without
inflating routine copy. You never invent facts that are not in the headline you are given."""

PROMPT = """
FIELDS
  main_title            A clean neutral rewrite of the headline. Strip the outlet name, ALL CAPS,
                        emoji, and clickbait framing ("You won't believe...", "Here's why...").
                        Keep it under 120 characters.
  one_sentence_summary  One sentence saying what happened, who is involved, and where. It must add
                        something beyond restating main_title. If the headline is too vague to say
                        more, stay vague - do not guess details.
  countries_or_actors   Named states, organisations, companies or people driving the story.
                        Empty list if the headline names none. Do not infer.
  locations             Where the event happens. Use "global" only when it genuinely has no
                        geographic centre. Empty list if unknown.

CATEGORY - pick by what the story IS ABOUT, not by a single dramatic word in it.
  conflict     Armed violence between organised groups: war, strikes, militias, terrorism,
               insurgency. NOT accidents, NOT disasters, NOT crime, NOT arguments.
  politics     Government, elections, diplomacy, courts and law, sanctions, migration policy.
  economy      Markets, trade, companies, jobs, prices, budgets, debt.
  technology   Software, internet platforms, AI, chips, telecoms, cybersecurity.
  science      Research findings, space, mathematics, archaeology.
  environment  Climate, weather, wildfires, drought, ecosystems, pollution.
  health       Disease, medicine, hospitals, public health.
  society      Everything else about people and daily life: sport, culture, music, film, books,
               food and recipes, reviews, celebrity, education, religion, crime and trials,
               accidents and transport disasters, human interest.
  If a story is a review, a recipe, a sports result or a profile, the answer is `society` -
  whatever the subject matter is about.

LIFE_IMPACT - which part of an ordinary person's life this story could change. Pick the single
strongest one. Judge the story's effect, not its subject matter.
  prices    Cost of food, fuel, housing, currency, taxes, interest rates.
  work      Jobs, wages, hiring, layoffs, business conditions, strikes over pay.
  movement  Borders, visas, travel, migration, transport, shipping routes.
  safety    Violence, crime, disaster or war risk to people where they live.
  services  Health care, electricity, water, internet, schooling, public transport.
  rights    Law, courts, speech, privacy, surveillance, voting, civil liberties.
  none      Nothing in ordinary life changes because of this. Reviews, sport, culture,
            celebrity, obituaries, human interest, curiosities, and the fate of one named
            person. Use this freely - most headlines are `none`.

STAGE - how far along the thing actually is. Read the verb.
  happened   It occurred: an attack, a death toll, a result, a collapse, an arrival.
  decided    A binding decision was taken: a law passed, a ruling issued, a rate set, a deal
             signed, a sentence handed down.
  proposed   Someone formally put it forward but it is not yet binding: a bill, a plan, a demand.
  discussed  Talk about a thing rather than the thing: analysis, opinion, a warning, a preview,
             a review, "X says", "Y calls for", "could", "may".

PEOPLE_AFFECTED_STATED - copy the number of PEOPLE the headline explicitly states are killed,
injured, ill, missing, displaced or evacuated. This is transcription, not estimation.
  Write 0 if the headline states no such number. 0 is the correct answer for most headlines.
  Only count people harmed. Sums of money, debts, contract values, fines, years, ages, scores,
  prices, crowd sizes and quantities of objects are all 0.
  For vague words use: "dozens" = 30, "hundreds" = 300, "thousands" = 3000.
  Never infer a number that is not there.

URGENCY - how fast this matters.
  high    Unfolding now, a reader may need to know within hours: ongoing attack, evacuation,
          market halt, breaking casualty report, imminent deadline.
  medium  Developing over days: a decision just taken, a trial under way, a storm approaching.
  low     Not time-bound: analysis, feature, retrospective, review, profile.

EXAMPLES:

Headline: "Russian strike on Kharkiv apartment block kills 14, regional governor says"
{{"main_title":"Russian strike on Kharkiv apartment block kills 14","one_sentence_summary":"A Russian
missile hit a residential building in Kharkiv, killing at least 14 people according to the regional
governor.","category":"conflict","life_impact":"safety","stage":"happened",
"people_affected_stated":14,"urgency":"high","countries_or_actors":["Russia","Ukraine"],
"locations":["Kharkiv","Ukraine"]}}

Headline: "Dickovers, baggravation and botiquette: 18 new words to describe our tech hellscape"
{{"main_title":"Eighteen new words coined to describe modern technology frustrations",
"one_sentence_summary":"A feature proposes eighteen new terms for common irritations of everyday
technology use.","category":"society","life_impact":"none","stage":"discussed",
"people_affected_stated":0,"urgency":"low","countries_or_actors":[],"locations":[]}}

Headline: "Tunisian parliament passes 2027 budget after three days of debate"
{{"main_title":"Tunisian parliament passes 2027 budget","one_sentence_summary":"Tunisia's parliament
approved the 2027 budget following three days of debate.","category":"economy",
"life_impact":"prices","stage":"decided","people_affected_stated":0,"urgency":"medium",
"countries_or_actors":["Tunisia"],"locations":["Tunisia"]}}


Headline: {title}
Outlet: {source}
Now score the headline above."""
 
async def embedding(text: str):
    body= {'model': 'nomic-embed-text','input': text}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response= await client.post('http://localhost:11434/api/embed', json=body)
    return response.json()["embeddings"][0]

async def generate_cluster(article: Article):
    body= {'model': 'qwen2.5:3b' ,"stream": False,"system": SYSTEM,"prompt": PROMPT.format(title=article.title,source=article.source),"format": CLUSTER_SCHEMA,"options": {"temperature":0,"num_predict": 400}         }
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post('http://localhost:11434/api/generate', json=body)
    return response.json()["response"]
