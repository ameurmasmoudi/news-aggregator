TOPIC_WEIGHT   = {"technology": 1.3, "economy": 1.2, "politics": 1.0, "health": 1.0,
                  "science": 1.0, "environment": 1.0, "conflict": 0.9, "society": 0.7}
IMPACT_WEIGHT  = {"prices": 1.0, "work": 1.0, "services": 0.9, "movement": 0.8,
                  "rights": 0.8, "safety": 0.7, "none": 0.0}
STAGE_WEIGHT   = {"happened": 1.0, "decided": 0.9, "proposed": 0.5, "discussed": 0.25}
URGENCY_WEIGHT = {"high": 1.0, "medium": 0.5, "low": 0.0}
PART_WEIGHT    = {"impact": 0.30, "coverage": 0.20, "stage": 0.15,
                  "toll": 0.15, "urgency": 0.10, "novelty": 0.10}

HALF_LIFE_HOURS       = 48.0
STORY_HALF_LIFE_HOURS = 72.0
COVERAGE_CAP          = 6
TOLL_LOG_DIVISOR      = 4.5
