# the quote-check
# since the evaluator can fabricate or paraphrase "evidence", so we verify each quote actually
# appears in the transcript. If it doesn't, we drop it and flag it. 

import re

def norm(s: str) -> str:
    # lowercase + removes whitespace
    return re.sub(r"\s+", " ", (s or "")).strip().lower()

def verify(items: list[dict], transcript_text: str) -> list[dict]:
    tt = norm(transcript_text)
    for item in items:
        quote = norm(item.get("evidence", ""))
        found = bool(quote) and quote in tt
        item["evidence_verified"] = found
        if not found:
            item["evidence"] = None  # drop the unverifiable quote
    return items
