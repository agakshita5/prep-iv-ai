# shared groq setup for the scoring workflow.
# reduces "self-preference" bias

import json
import os
from functools import lru_cache

from groq import Groq

INTERVIEW_MODEL = "llama-3.3-70b-versatile"
EVAL_MODEL = "openai/gpt-oss-120b" 
REPORT_MODEL = "llama-3.3-70b-versatile"

@lru_cache(maxsize=1)
def _client() -> Groq:
    return Groq(api_key=os.environ["GROQ_API_KEY"])

# call groq and force a json object back, then parse it
def groq_json(model: str, system_prompt: str, user_prompt: str) -> dict:
    resp = _client().chat.completions.create(
        model=model,
        temperature=0.2, # low temperature keeps grading consistent
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return json.loads(resp.choices[0].message.content)
