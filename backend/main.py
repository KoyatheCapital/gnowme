from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any
import os

from config import Config
from core.internal_monologue import InternalMonologueGenerator
from intelligence.consciousness_translator import ConsciousnessTranslator
from voice.voxtral import GnowmeVoice
from core.agent_schema import AgentContextPayload
from core import speech_engine

app = FastAPI(title="Gnowme")

# Serve web frontend
_frontend = os.path.join(os.path.dirname(__file__), "..", "frontend", "web")
if os.path.isdir(_frontend):
    app.mount("/static", StaticFiles(directory=_frontend), name="static")

@app.get("/ui", include_in_schema=False)
async def serve_ui():
    return FileResponse(os.path.join(_frontend, "index.html"))

voice_engine = GnowmeVoice(Config.MISTRAL_API_KEY, Config.USER_VOICE_REF)

translators:  Dict[str, ConsciousnessTranslator]   = {}
generators:   Dict[str, InternalMonologueGenerator] = {}
voice_paths:  Dict[str, str] = {}  # user_id → wav path

def get_translator(uid: str) -> ConsciousnessTranslator:
    if uid not in translators:
        translators[uid] = ConsciousnessTranslator(uid)
    return translators[uid]

def get_generator(uid: str) -> InternalMonologueGenerator:
    if uid not in generators:
        generators[uid] = InternalMonologueGenerator(uid)
    return generators[uid]

# ══════════════════════════ MORNING WAKE SEQUENCE ══════════════════════════

class WakeStepRequest(BaseModel):
    user_id: str
    step: int = 0

@app.post("/morning/wake/step")
async def wake_step(request: WakeStepRequest):
    """Return the next line(s) in the morning wake sequence."""
    step = speech_engine.get_wake_step(request.step)
    return {
        "step": request.step,
        "id": step["id"],
        "lines": step["lines"],
        "wait_for_response": step["wait_for_response"],
        "done": step["id"] == "done",
        "script": "\n".join(step["lines"]),
    }

# ══════════════════════════ GUIDANCE ══════════════════════════

class GuidanceRequest(BaseModel):
    user_id: str
    bio_state: Dict[str, Any] = {}
    context:   Dict[str, Any] = {}
    user_input: str = ""

@app.post("/speak/guidance")
async def speak_guidance(request: GuidanceRequest):
    gen = get_generator(request.user_id)
    monologue = await gen.generate(request.bio_state, request.context, request.user_input)
    return {"monologue": monologue}

@app.post("/morning/flow")
async def morning_flow(request: GuidanceRequest):
    gen = get_generator(request.user_id)
    monologue = await gen.morning_flow(request.bio_state, request.context)
    return {"monologue": monologue}

@app.post("/speak/midday")
async def midday(request: GuidanceRequest):
    gen = get_generator(request.user_id)
    monologue = await gen.midday(request.bio_state, request.context)
    return {"monologue": monologue}

@app.post("/speak/decision")
async def decision_moment(request: GuidanceRequest):
    gen = get_generator(request.user_id)
    monologue = await gen.decision_moment(request.bio_state, request.context)
    return {"monologue": monologue}

@app.post("/speak/evening")
async def evening(request: GuidanceRequest):
    gen = get_generator(request.user_id)
    monologue = await gen.evening(request.bio_state, request.context)
    return {"monologue": monologue}

# ══════════════════════════ BOOKS ══════════════════════════

class AddBookRequest(BaseModel):
    user_id: str
    book_id: str
    source_path: str | None = None
    priority: str = "primary"

@app.post("/books/add")
async def add_book(request: AddBookRequest):
    try:
        t = get_translator(request.user_id)
        t.activate_book(request.book_id, request.source_path, priority=request.priority)
        return {
            "status": "success",
            "active_books": t.active_books,
            "background_books": t.background_books,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════ VOICE CLONE ══════════════════════════

class VoiceCloneRequest(BaseModel):
    user_id: str

@app.post("/voice/clone")
async def clone_voice(user_id: str, file: UploadFile = File(...)):
    """Upload voice WAV → store as user reference for Voxtral TTS."""
    try:
        os.makedirs("data/voice", exist_ok=True)
        path = f"data/voice/{user_id}_ref.wav"
        content = await file.read()
        with open(path, "wb") as f:
            f.write(content)
        voice_paths[user_id] = path
        return {
            "status": "success",
            "message": "Voice cloned. All guidance will now sound like you.",
            "voice_path": path,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voice/status/{user_id}")
async def voice_status(user_id: str):
    has_voice = os.path.exists(f"data/voice/{user_id}_ref.wav")
    return {"has_voice": has_voice, "user_id": user_id}

# ══════════════════════════ AGENTS ══════════════════════════

@app.post("/agents/context")
async def ingest_agent_context(payload: AgentContextPayload):
    try:
        gen = get_generator(payload.user_id)
        context = {
            "work_summary": payload.work_summary,
            "detected_human_state": payload.detected_human_state,
            "activity_type": payload.current_activity_type,
            "domain": payload.domain,
            "agent_context": True,
        }
        monologue = await gen.real_time_flow({}, context, payload.work_summary)
        return {"status": "received", "monologue_preview": monologue[:200]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════ CONFLICT ══════════════════════════

class ConflictResponse(BaseModel):
    user_id: str
    user_choice: str
    original_context: Dict

@app.post("/conflict/resolve")
async def resolve_conflict(request: ConflictResponse):
    gen = get_generator(request.user_id)
    monologue = await gen.handle_conflict_response(request.user_id, request.user_choice, request.original_context)
    return {"status": "resolved", "monologue": monologue}

# ══════════════════════════ HEALTH ══════════════════════════

@app.get("/")
async def root():
    return {"status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
