import os
from functools import lru_cache
from supabase import create_client, Client

@lru_cache(maxsize=1)
def client() -> Client:
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SECRET_KEY"],
    )

# fetch one interview row by id
def get_interview(interview_id: str) -> dict | None:
    resp = (
        client()
        .table("interviews")
        .select("*")
        .eq("id", interview_id)
        .maybe_single()  # returns None instead of raising when not found
        .execute()
    )
    return resp.data


# append one transcript turn
def insert_turn(interview_id: str, speaker: str, text: str) -> None:
    if not text:
        return
    (
        client()
        .table("transcript_turns")
        .insert({"interview_id": interview_id, "speaker": speaker, "text": text})
        .execute()
    )

# fetch oldest transcript 
def get_transcript(interview_id: str) -> list[dict]: 
    resp = (
        client()
        .table("transcript_turns")
        .select("*")
        .eq("interview_id", interview_id)
        .order("created_at")
        .execute()
    )
    return resp.data or []

def save_evaluation( interview_id: str, candidate_report: dict | None, recruiter_report: dict | None, overall_score: int | None, recommendation: str | None) -> None:
    # upsert: re-scoring overwrites the old report
    (
        client()
        .table("evaluations")
        .upsert(
            {
                "interview_id": interview_id,
                "candidate_report": candidate_report,
                "recruiter_report": recruiter_report,
                "overall_score": overall_score,
                "recommendation": recommendation,
            }
        )
        .execute()
    )
