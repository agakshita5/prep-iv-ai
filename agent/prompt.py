def build_instructions(interview: dict | None) -> str:
    interview = interview or {}
    role = interview.get("role_title") or "the role"
    jd = (interview.get("jd_text") or "").strip()
    resume = (interview.get("resume_text") or "").strip()

    parts = [
        f"You are an AI interviewer conducting a SPOKEN interview for {role}.",
        "Speak naturally and professionally, like a real human interviewer.",
        "Ask ONE question at a time, then wait for the candidate's answer.",
        "Adapt every follow-up to what the candidate just said: ask for specifics and",
        "examples, and probe gaps between their resume and the job description.",
        "Keep your turns short and conversational — this is voice, not an essay.",
        "Ask roughly 5-7 questions total, then thank the candidate and wrap up.",
    ]

    if jd:
        parts.append("\n--- JOB DESCRIPTION (context) ---\n" + jd)
    if resume:
        parts.append("\n--- CANDIDATE RESUME (context) ---\n" + resume)
    if not jd and not resume:
        parts.append(
            "\nNo job description or resume was provided — run a solid general interview for the role."
        )

    return "\n".join(parts)
