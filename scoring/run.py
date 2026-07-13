# orchestrator — runs the fixed scoring pipeline once at interview end
# evaluate -> verify -> insights -> reports -> save, once

import logging
from db import get_interview, get_transcript, save_evaluation, set_iv_status
from .evaluator import evaluate, format_transcript
from .verify import verify
from .insights import speaking_insights, qa_pairs
from .report_prompts import build_candidate_report, build_recruiter_report

logger = logging.getLogger("prepiv-scoring")

def run_scoring(interview_id: str) -> None:
    turns = get_transcript(interview_id)
    if not turns:
        logger.info("no transcript for %s; skipping scoring", interview_id)
        return

    interview = get_interview(interview_id) or {}

    scored = evaluate(turns)                                # 1. evaluate -> scores + evidence
    scored = verify(scored, format_transcript(turns))       # 2. drop unverifiable quotes
    insights = speaking_insights(turns)                     # measured speaking metrics (fillers, pace)

    if interview.get("recruiter_id"):
        recruiter_report = build_recruiter_report(scored, interview)
        candidate_report = None
        recommendation = recruiter_report.get("recommendation") # string
        overall = None # int /100
    else:
        candidate_report = build_candidate_report(scored, insights)
        candidate_report["questions"] = qa_pairs(turns)
        recruiter_report = None
        overall = candidate_report.get("overall_score") 
        recommendation = None

    save_evaluation(
        interview_id,
        candidate_report=candidate_report,
        recruiter_report=recruiter_report,
        overall_score=overall,          
        recommendation=recommendation,  
    )

    set_iv_status(interview_id, "completed")

    logger.info("scoring complete for %s", interview_id)
