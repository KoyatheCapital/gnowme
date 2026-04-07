# Gnowme

A **Personal Consciousness Extension** — a calm, always-present companion that helps you stay in a strong, driven, and resilient mindset throughout the day.

## What It Does

- Delivers guidance in **your own cloned voice** (Mistral Voxtral TTS)
- Uses **book consciousness modules** (Rich Dad Poor Dad, Art of War, Atomic Habits, etc.) to shape your human mindset
- Agents provide high-level context about what you're working on so Gnowme can time its support better
- Safety and restraint are core — daily intervention limits, confidence thresholds, CCI entry protocol

## Architecture

```
backend/
├── core/           # CCI, internal monologue, agent schema, stoic knowledge
├── intelligence/   # Consciousness translator, per-user RAG
├── state_engine/   # Biometric state classification
├── trust/          # Intervention budget and trust profile
└── voice/          # Mistral Voxtral TTS with voice cloning

frontend/
└── ios/            # SwiftUI minimal UI

scripts/            # Safety and integration tests
```

## Setup

1. Copy `.env.example` to `.env` and fill in your keys
2. Add a 5–10 second voice recording to `data/voice/user_ref.wav`
3. Start Postgres: `docker compose up -d`
4. Install deps: `pip install -r backend/requirements.txt`
5. Run backend: `uvicorn backend.main:app --reload`
6. Run tests: `python scripts/test_full_day_safety.py`

## Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/books/add` | Activate a book consciousness module |
| POST | `/agents/context` | Receive context from external agents |
| POST | `/speak/guidance` | Generate + speak mindset guidance |
| POST | `/morning/flow` | Morning ritual guidance |
| GET | `/` | Health check |
