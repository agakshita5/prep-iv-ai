#  measured speaking metrics like fillers, pace

import re
from datetime import datetime

# common spoken fillers to count
FILLERS = ["um", "uh", "er", "hmm", "like", "you know", "i mean", "actually", "basically", "literally"]

def parse_ts(s: str | None) -> datetime | None:
    try:
        return datetime.fromisoformat((s or "").replace("Z", "+00:00"))
    except ValueError:
        return None


def speaking_insights(turns: list[dict]) -> dict:
    user_turns = [t for t in turns if t["speaker"] == "user"]
    text = " ".join(t["text"] for t in user_turns).lower()
    total_words = len(re.findall(r"[a-z']+", text))

    # count each filler phrase that actually appeared
    found = {}
    for f in FILLERS:
        n = len(re.findall(r"\b" + re.escape(f) + r"\b", text))
        if n:
            found[f] = n
    filler_count = sum(found.values())

    wpm = None
    times = [t for t in (parse_ts(x.get("created_at")) for x in user_turns) if t]
    if len(times) >= 2 and total_words:
        minutes = (max(times) - min(times)).total_seconds() / 60
        if minutes > 0:
            wpm = round(total_words / minutes)

    return {
        "words_per_minute": wpm,    # approximate; None if not computable
        "total_words": total_words,
        "answers": len(user_turns),
        "filler_words": {"count": filler_count, "examples": found},
        "interruptions": None,  # TODO: needs barge-in logging from the agent
    }