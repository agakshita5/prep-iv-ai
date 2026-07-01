# EVAL_MODEL reads the transcript and returns a score + a candidate quote as evidence for each competency

from .config import EVAL_MODEL, groq_json
from .rubric import RUBRIC

# turn DB rows into readable lines
def format_transcript(turns: list[dict]) -> str:
    lines = []
    for t in turns:
        speaker = "Candidate" if t["speaker"] == "user" else "Interviewer"
        lines.append(f"{speaker}: {t['text']}")
    return "\n".join(lines)


def evaluate(turns: list[dict]) -> list[dict]:
    transcript = format_transcript(turns)
    rubric_text = "\n".join(f"• {name}: {anchors}" for name, anchors in RUBRIC.items())

    # system_prompt: model's persistent role and rules
    system_prompt = "You are a strict, fair interview grader. You grade the CANDIDATE only, using ONLY the transcript as evidence. Respond with a JSON object."
    # user_prompt: per-call task and data
    user_prompt = f"""Grade the candidate on each competency below (score 1-5) using this rubric:
        {rubric_text}

        Rules:
        - Give an integer score 1-5 AND an "evidence" field that is a DIRECT, VERBATIM quote
        of the CANDIDATE's own words copied exactly from the transcript.
        - If the candidate never demonstrated a competency, set "not_assessed": true and
        "score": null. Do NOT guess, and do NOT invent quotes.

        Return this JSON shape:
        {{"competencies": [
            {{"competency": "<name>", 
            "score": <1-5 or null>, 
            "not_assessed": <true|false>,
            "evidence": "<verbatim candidate quote, or empty string>",
            "reasoning": "<one short sentence>"}}
        ]}}

        TRANSCRIPT:
        {transcript}
    """
    data = groq_json(EVAL_MODEL, system_prompt, user_prompt)
    return data.get("competencies", [])
