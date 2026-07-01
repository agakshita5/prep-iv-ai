import asyncio
import logging
from dotenv import load_dotenv
from livekit.agents import ( Agent, AgentSession, JobContext, WorkerOptions, cli, ConversationItemAddedEvent )
from livekit.agents.llm import ChatMessage # represent one msg in the conversation
from livekit.plugins import groq
from db import get_interview, insert_turn
from .prompt import build_instructions
from scoring.run import run_scoring

load_dotenv()
logger = logging.getLogger("prepiv-agent")

async def entrypoint(ctx: JobContext):
    # join the room this job was dispatched to
    await ctx.connect()

    # room name is the interview uuid -> load its role/JD/resume for an adaptive prompt
    interview_id = ctx.room.name
    interview = await asyncio.to_thread(get_interview, interview_id)
    logger.info("starting interview %s", interview_id)

    # when the interview ends, generate + save the reports.
    async def on_shutdown():
        await asyncio.to_thread(run_scoring, interview_id)

    ctx.add_shutdown_callback(on_shutdown)

    # whole realtime pipeline
    session = AgentSession(
        stt=groq.STT(model="whisper-large-v3-turbo", language="en"),
        llm=groq.LLM(model="llama-3.3-70b-versatile"),
        tts=groq.TTS(model="canopylabs/orpheus-v1-english", voice="diana"),
    )

    # persist every finalized turn to Supabase for the report
    @session.on("conversation_item_added")
    def on_item(ev: ConversationItemAddedEvent):
        if not isinstance(ev.item, ChatMessage):
            return
        text = ev.item.text_content
        if not text:
            return
        speaker = "user" if ev.item.role == "user" else "ai"
        # supabase-py is sync; so asyncio writes msg asynchronously to supabase
        asyncio.create_task(
            asyncio.to_thread(insert_turn, interview_id, speaker, text) # runs the database insert in a separate thread
        )

    await session.start(
        agent=Agent(instructions=build_instructions(interview)),
        room=ctx.room,
    )

    # AI speaks first: greet + ask question one
    await session.generate_reply(
        instructions=(
            "Greet the candidate warmly, briefly introduce yourself as their AI "
            "interviewer, and ask your first question."
        )
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
