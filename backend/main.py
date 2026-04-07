from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os

from config import Config
from core.internal_monologue import InternalMonologueGenerator
from intelligence.consciousness_translator import ConsciousnessTranslator
from voice.voxtral import GnowmeVoice
from core.agent_schema import AgentContextPayload
from core import speech_engine

app = FastAPI(title="Gnowme")

# ── Frontend ────────────────────────────────────────────────────────────────
_frontend = os.path.join(os.path.dirname(__file__), "..", "frontend", "web")
if os.path.isdir(_frontend):
    app.mount("/static", StaticFiles(directory=_frontend), name="static")

@app.get("/ui", include_in_schema=False)
async def serve_ui():
    return FileResponse(os.path.join(_frontend, "index.html"))

# ── Per-user registries ─────────────────────────────────────────────────────
translators:    Dict[str, ConsciousnessTranslator]    = {}
generators:     Dict[str, InternalMonologueGenerator] = {}
voice_engines:  Dict[str, GnowmeVoice]               = {}

# Default (shared) voice engine — used until user records their own voice
_default_voice = GnowmeVoice(Config.MISTRAL_API_KEY, Config.USER_VOICE_REF)


def get_translator(uid: str) -> ConsciousnessTranslator:
    if uid not in translators:
        translators[uid] = ConsciousnessTranslator(uid)
    return translators[uid]


def get_generator(uid: str) -> InternalMonologueGenerator:
    if uid not in generators:
        generators[uid] = InternalMonologueGenerator(uid)
    return generators[uid]


def get_voice(uid: str) -> GnowmeVoice:
    """Return the user's personal voice engine, or the default if none recorded."""
    if uid in voice_engines:
        return voice_engines[uid]
    personal_path = f"data/voice/{uid}_ref.wav"
    if os.path.exists(personal_path):
        voice_engines[uid] = GnowmeVoice(Config.MISTRAL_API_KEY, personal_path)
        return voice_engines[uid]
    return _default_voice


# ══════════════════════════════════════════════════════════════════════
# MORNING WAKE SEQUENCE
# ══════════════════════════════════════════════════════════════════════

class WakeStepRequest(BaseModel):
    user_id: str
    step: int = 0

@app.post("/morning/wake/step")
async def wake_step(request: WakeStepRequest):
    """Return the next step in the 6-part morning wake conversation."""
    step = speech_engine.get_wake_step(request.step)
    return {
        "step":              request.step,
        "id":                step["id"],
        "lines":             step["lines"],
        "wait_for_response": step["wait_for_response"],
        "done":              step["id"] == "done",
        "script":            "\n".join(step["lines"]),
    }


# ══════════════════════════════════════════════════════════════════════
# GUIDANCE ENDPOINTS
# ══════════════════════════════════════════════════════════════════════

class GuidanceRequest(BaseModel):
    user_id: str
    bio_state:  Dict[str, Any] = {}
    context:    Dict[str, Any] = {}
    user_input: str = ""
    feedback:   Optional[Dict[str, Any]] = None  # learning signal

@app.post("/speak/guidance")
async def speak_guidance(request: GuidanceRequest):
    gen = get_generator(request.user_id)
    monologue = await gen.generate(
        request.bio_state,
        request.context,
        request.user_input,
        feedback=request.feedback,
    )
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


# ══════════════════════════════════════════════════════════════════════
# BOOKS
# ══════════════════════════════════════════════════════════════════════

class AddBookRequest(BaseModel):
    user_id:     str
    book_id:     str
    source_path: Optional[str] = None
    priority:    str = "primary"

@app.post("/books/add")
async def add_book(request: AddBookRequest):
    try:
        t = get_translator(request.user_id)
        t.activate_book(request.book_id, request.source_path, priority=request.priority)
        return {
            "status":           "success",
            "active_books":     t.active_books,
            "background_books": t.background_books,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════════════
# VOICE CLONE  — upload → save persistently → hot-reload engine
# ══════════════════════════════════════════════════════════════════════

@app.post("/voice/clone")
async def clone_voice(
    user_id: str = Query(..., description="User identifier"),
    file: UploadFile = File(...),
):
    """
    Upload a WAV voice sample.
    Saves it permanently for the user and hot-reloads their voice engine
    so every subsequent TTS call uses this reference immediately.
    """
    try:
        os.makedirs("data/voice", exist_ok=True)
        path    = f"data/voice/{user_id}_ref.wav"
        content = await file.read()

        if len(content) < 1000:
            raise HTTPException(status_code=400, detail="Recording too short — minimum ~2 seconds")

        with open(path, "wb") as f:
            f.write(content)

        # Hot-reload or create the user's personal voice engine
        if user_id in voice_engines:
            voice_engines[user_id].reload_ref(path)
        else:
            voice_engines[user_id] = GnowmeVoice(Config.MISTRAL_API_KEY, path)

        return {
            "status":  "success",
            "message": "Your voice has been cloned. All future guidance will sound like you.",
            "voice_path": path,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/voice/status/{user_id}")
async def voice_status(user_id: str):
    path      = f"data/voice/{user_id}_ref.wav"
    has_voice = os.path.exists(path) and os.path.getsize(path) > 0
    return {"has_voice": has_voice, "user_id": user_id}


# ══════════════════════════════════════════════════════════════════════
# TTS — returns audio bytes using user's cloned voice
# ══════════════════════════════════════════════════════════════════════

class TTSRequest(BaseModel):
    user_id: str
    text:    str
    style:   str = "grounded"

@app.post("/tts/speak")
async def tts_speak(request: TTSRequest):
    """Generate audio for text using the user's cloned voice (or default)."""
    try:
        voice = get_voice(request.user_id)
        audio = await voice.speak(request.text, request.style)
        from fastapi.responses import Response
        return Response(content=audio, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════════════
# AGENT CONTEXT INGEST
# ══════════════════════════════════════════════════════════════════════

@app.post("/agents/context")
async def ingest_agent_context(payload: AgentContextPayload):
    try:
        gen = get_generator(payload.user_id)
        context = {
            "work_summary":          payload.work_summary,
            "detected_human_state":  payload.detected_human_state,
            "activity_type":         payload.current_activity_type,
            "domain":                payload.domain,
            "agent_context":         True,
        }
        monologue = await gen.real_time_flow({}, context, payload.work_summary)
        return {"status": "received", "monologue_preview": monologue[:200]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════════════
# FEEDBACK — learning signal from client
# ══════════════════════════════════════════════════════════════════════

class FeedbackRequest(BaseModel):
    user_id:      str
    interrupted:  bool = False
    followed:     bool = False
    skipped_fast: bool = False

@app.post("/feedback")
async def receive_feedback(request: FeedbackRequest):
    """Send interaction feedback so the monologue style can adapt over time."""
    gen = get_generator(request.user_id)
    gen._update_learned_style({
        "interrupted":  request.interrupted,
        "followed":     request.followed,
        "skipped_fast": request.skipped_fast,
    })
    return {"status": "learned"}


# ══════════════════════════════════════════════════════════════════════
# CONFLICT RESOLUTION
# ══════════════════════════════════════════════════════════════════════

class ConflictResponse(BaseModel):
    user_id:          str
    user_choice:      str
    original_context: Dict

@app.post("/conflict/resolve")
async def resolve_conflict(request: ConflictResponse):
    gen = get_generator(request.user_id)
    monologue = await gen.handle_conflict_response(
        request.user_id, request.user_choice, request.original_context
    )
    return {"status": "resolved", "monologue": monologue}


# ══════════════════════════════════════════════════════════════════════
# HEALTH
# ══════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {"status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
