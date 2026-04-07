import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from config import Config
from core.internal_monologue import InternalMonologueGenerator
from intelligence.consciousness_translator import ConsciousnessTranslator
from intelligence.rag import UserRAG
from voice.voxtral import GnowmeVoice
from core.agent_schema import AgentContextPayload
from state_engine.engine import StateEngine, Biometrics

app = FastAPI(title="Gnowme")

voice_engine = GnowmeVoice(Config.MISTRAL_API_KEY, Config.USER_VOICE_REF)

# In-memory stores for demo
translators = {}
monologue_generators = {}

def get_translator(user_id: str):
    if user_id not in translators:
        translators[user_id] = ConsciousnessTranslator(user_id)
    return translators[user_id]

def get_monologue_generator(user_id: str):
    if user_id not in monologue_generators:
        monologue_generators[user_id] = InternalMonologueGenerator(user_id)
    return monologue_generators[user_id]

# ====================== BOOK GALLERY & CONSCIOUSNESS ======================

class AddBookRequest(BaseModel):
    user_id: str
    book_id: str
    source_path: str | None = None

@app.post("/books/add")
async def add_book(request: AddBookRequest):
    """Activate a book's consciousness module"""
    try:
        translator = get_translator(request.user_id)
        translator.activate_book(request.book_id, request.source_path)
        return {
            "status": "success",
            "message": f"Consciousness module '{request.book_id}' activated.",
            "active_books": translator.active_books
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====================== AGENT CONNECTIVITY ======================

@app.post("/agents/context")
async def ingest_agent_context(payload: AgentContextPayload):
    """High-level context from agents → better human mindset timing"""
    try:
        generator = get_monologue_generator(payload.user_id)
        context = {
            "work_summary": payload.work_summary,
            "detected_human_state": payload.detected_human_state,
            "activity_type": payload.current_activity_type,
            "domain": payload.domain,
            "agent_context": True
        }
        monologue = await generator.real_time_flow({}, context, payload.work_summary)
        audio = await voice_engine.speak(monologue)
        return {
            "status": "received",
            "human_guidance_generated": True,
            "monologue_preview": monologue[:200] + "..."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====================== GUIDANCE ENDPOINTS ======================

class GuidanceRequest(BaseModel):
    user_id: str
    bio_state: Dict[str, Any] = {}
    context: Dict[str, Any] = {}
    user_input: str = ""

@app.post("/speak/guidance")
async def speak_guidance(request: GuidanceRequest):
    generator = get_monologue_generator(request.user_id)
    monologue = await generator.generate(request.bio_state, request.context, request.user_input)
    audio = await voice_engine.speak(monologue)
    return {"monologue": monologue, "audio_length": len(audio)}

@app.post("/morning/flow")
async def morning_flow(request: GuidanceRequest):
    generator = get_monologue_generator(request.user_id)
    monologue = await generator.morning_flow(request.bio_state, request.context)
    audio = await voice_engine.speak(monologue)
    return {"monologue": monologue, "audio_length": len(audio)}

# ====================== HEALTH ======================

@app.get("/")
async def root():
    return {"message": "Gnowme is running with full safety layers."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
