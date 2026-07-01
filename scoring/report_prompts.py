import json
from .config import REPORT_MODEL, groq_json

def build_candidate_report(scored: list[dict], insights: dict) -> dict:
    system_prompt = (
        "You are a supportive interview coach writing a growth-focused report for the CANDIDATE. "
        "Base every point ONLY on the given scores, verified evidence, and insights. Respond with a JSON object."
    )
    user_prompt = f"""Verified competency scores + evidence:
        {json.dumps(scored, indent=2)}

        Measured speaking insights:
        {json.dumps(insights, indent=2)}

        Write a JSON object with these fields:
        - overall_score: integer 0-100 (holistic, derived from the competency scores)
        - competencies: [{{"name", "score" (1-5 or null), "evidence", "comment"}}]
        - strengths: [short strings]
        - improvement_areas: [short strings]
        - transcript_highlights: [{{"quote", "comment"}}]  (use only verified quotes)
        - speaking_insights: echo the measured values + a one-line takeaway
        - personalized_feedback: 2-3 encouraging sentences
        - improvement_plan: [{{"action", "why"}}]
    """
    return groq_json(REPORT_MODEL, system_prompt, user_prompt)


def build_recruiter_report(scored: list[dict], interview: dict) -> dict:
    jd = (interview.get("jd_text") or "").strip() or "(none provided)"
    system_prompt = (
        "You are an objective hiring assistant. Judge the candidate's DEMONSTRATED potential from the interview. "
        "Use the job description only as CONTEXT, never as a keyword checklist. "
        "Base everything on the scores and verified evidence. "
        "Respond with a JSON object."
    )
    user_prompt = f"""Verified competency scores + evidence:
        {json.dumps(scored, indent=2)}

        Job description (context only):
        {jd}

        Write a JSON object with these fields:
        - recommendation: "hire" | "maybe" | "reject"
        - confidence: integer 0-100
        - competencies: [{{"name", "score", "evidence"}}]
        - strengths: [{{"point", "evidence"}}]
        - summary: 2-3 sentence interview summary
        - role_alignment: short paragraph on fit for the role
        - skills_demonstrated: [strings]
        - skills_limited_evidence: [strings]
        - skills_not_assessed: [strings]
        - areas_to_probe: [strings]   (for the next round)
        - hiring_rationale: 2-3 sentences
    """
    return groq_json(REPORT_MODEL, system_prompt, user_prompt)
