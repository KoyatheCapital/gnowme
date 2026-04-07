import asyncio
import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Mock the RAG/DB layer so tests run without Postgres or embedding API
mock_rag = MagicMock()
mock_rag.return_value.query.return_value = "Stay steady. Focus on what you control."
mock_rag.return_value.add_book.return_value = None
sys.modules["intelligence.rag"] = MagicMock(UserRAG=mock_rag)

from state_engine.engine import StateEngine, Biometrics
from trust.controller import TrustProfile
from core.cci import ContextualCognitiveInterface
from core.stoic_knowledge import get_stoic_reframe
from core.agent_schema import AgentContextPayload
from intelligence.consciousness_translator import ConsciousnessTranslator
from core.internal_monologue import InternalMonologueGenerator

async def test_full_day():
    print("=== Gnowme Full-Day Safety Test ===\n")

    # ── 1. StateEngine ─────────────────────────────────────────────────────────
    print("1. StateEngine — Biometric Classification")
    engine = StateEngine()

    bio_low = Biometrics(hrv=38, heart_rate=95, resting_hr=62, sleep_score=55)
    state = engine.build_state(bio_low, {})
    print(f"   Low HRV + HR spike → state: {state['state']}, confidence: {state['confidence']}")
    assert state["state"] == "acute_pressure"

    bio_tired = Biometrics(hrv=60, heart_rate=65, resting_hr=62, sleep_score=58)
    state2 = engine.build_state(bio_tired, {})
    print(f"   Low sleep only    → state: {state2['state']}, tone: {state2['recommended_tone']}")
    assert state2["state"] == "low_energy"

    bio_fine = Biometrics(hrv=65, heart_rate=65, resting_hr=62, sleep_score=80)
    state3 = engine.build_state(bio_fine, {})
    print(f"   Baseline          → state: {state3['state']}")
    assert state3["state"] == "baseline"
    print("   PASS\n")

    # ── 2. TrustProfile ────────────────────────────────────────────────────────
    print("2. TrustProfile — Intervention Budget")
    trust = TrustProfile()
    assert trust.can_intervene() is True
    for _ in range(10):
        trust.record_intervention()
    assert trust.can_intervene() is False
    print("   Blocked after 10 interventions: PASS")
    trust.update_from_event("followed")
    trust.update_from_event("ignored")
    config = trust.adapt_config()
    print(f"   Adaptive config: {config}")
    print("   PASS\n")

    # ── 3. CCI Entry ───────────────────────────────────────────────────────────
    print("3. CCI — Respectful Entry")
    cci = ContextualCognitiveInterface()
    entry, consent = cci.enter("feeling stressed and under pressure", {"availability": "micro"})
    print(f"   Entry: {entry}")
    assert "20" in entry
    assert consent is True
    print("   PASS\n")

    # ── 4. Stoic Knowledge ─────────────────────────────────────────────────────
    print("4. Stoic Knowledge — Reframes")
    reframe = get_stoic_reframe("dichotomy_of_control", "acute_pressure")
    print(f"   Reframe: {reframe}")
    assert len(reframe) > 0
    print("   PASS\n")

    # ── 5. Book Priority & Conflict Detection ──────────────────────────────────
    print("5. ConsciousnessTranslator — Book Priority & Conflict Detection")
    translator = ConsciousnessTranslator("test_user")
    translator.activate_book("rich_dad_poor_dad", priority="primary")
    translator.activate_book("art_of_war", priority="primary")
    translator.activate_book("atomic_habits", priority="background")
    assert "rich_dad_poor_dad" in translator.active_books
    assert "atomic_habits" in translator.background_books
    conflict = translator.detect_conflict_and_resolve({})
    assert conflict == "conflict_detected"
    print(f"   Conflict detected correctly: PASS\n")

    # ── 6. Full Monologue Pipeline ─────────────────────────────────────────────
    print("6. InternalMonologue — Full Pipeline")
    generator = InternalMonologueGenerator("test_user")
    generator.translator.active_books = ["atomic_habits"]
    generator.translator.background_books = []

    bio_state = {"hrv": 52, "heart_rate": 68, "resting_hr": 62, "sleep_score": 58}
    context = {"work_summary": "preparing for a big presentation", "agent_context": True}
    monologue = await generator.generate(bio_state, context, "feeling a bit anxious")
    print(f"   Preview: {monologue[:250]}...")
    assert len(monologue) > 50
    print("   PASS\n")

    # ── 7. Morning Flow ────────────────────────────────────────────────────────
    print("7. Morning Flow")
    morning = await generator.morning_flow(bio_state, {})
    print(f"   {morning[:200]}...")
    print("   PASS\n")

    # ── 8. Daily Limit Respected ───────────────────────────────────────────────
    print("8. Daily Limit — Stepping Back After Max Interventions")
    fresh = InternalMonologueGenerator("test_user_2")
    fresh.translator.active_books = ["atomic_habits"]
    for _ in range(10):
        fresh.trust.record_intervention()
    result = await fresh.generate({}, {}, "")
    assert "Stepping back" in result
    print(f"   Response: '{result}' — PASS\n")

    print("=" * 50)
    print("ALL TESTS PASSED. Gnowme is ready.")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_full_day())
