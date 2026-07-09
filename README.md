# prep-iv-ai

Python LiveKit voice agent for PrepIV. It joins the interview room, conducts an
adaptive interview (role + JD + resume), and saves the transcript to Supabase.
Uses the **same** LiveKit + Supabase projects as the web app, plus a Groq key.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # fill in: copy LIVEKIT_* + SUPABASE_* from prep-iv/.env.local, add GROQ_API_KEY
```

## Run (dev)
```bash
python -m agent.worker dev
```
The worker connects to LiveKit Cloud and auto-joins each new interview room. Open an
interview in the web app and the agent will greet you and start asking questions.

## Layout
- `agent/worker.py` — the agent (STT -> LLM -> TTS loop + transcript persistence)
- `agent/prompt.py` — builds the adaptive system prompt from role/JD/resume
- `db.py` — Supabase reads/writes (same project as the web app)
- `scoring/` - scoring workflow
