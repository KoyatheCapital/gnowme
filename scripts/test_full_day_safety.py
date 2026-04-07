import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from intelligence.consciousness_translator import ConsciousnessTranslator
from core.internal_monologue import InternalMonologueGenerator
from state_engine.engine import StateEngine, Biometrics
from trust.controller import TrustProfile
from core.agent_schema import AgentContextPayload

async def test_full_day():
    user_id = "test_user_001"
    print("=== Gnowme Full-Day Safety Test ===\n")

    translator = ConsciousnessTranslator(user_id)
    translator.activate_book("rich_dad_poor_dad")
    translator.activate_book("art_of_war")
    print("Activated books:", translator.active_books)

    generator = InternalMonologueGenerator(user_id)
    state_engine = StateEngine()

    # Morning - Low Energy
    print("\n1. Morning - Low Energy")
    bio = Biometrics(hrv=52, heart_rate=68, resting_hr=62, sleep_score=58)
    context = {"time_of_day": "morning", "activity": "waking_up"}
    monologue = await generator.morning_flow(bio.__dict__, context)
    print(monologue[:400] + "...")

    # Midday - High Pressure via Agent Context
    print("\n2. Midday - High Pressure (Agent Context)")
    agent_payload = AgentContextPayload(
        user_id=user_id,
        agent_id="negotiation_agent",
        work_summary="Preparing high-stakes client negotiation",
        detected_human_state=["high_stakes", "decision_fatigue"],
        current_activity_type="meeting_prep",
        domain="sales"
    )
    context = {
        "work_summary": agent_payload.work_summary,
        "detected_human_state": agent_payload.detected_human_state,
        "agent_context": True
    }
    monologue = await generator.real_time_flow({}, context, "feeling pressure")
    print(monologue[:400] + "...")

    # Daily limit check
    print("\n3. Intervention Budget Check")
    trust = TrustProfile()
    for i in range(10):
        trust.record_intervention()
    result = trust.can_intervene()
    print(f"Can intervene after 10 calls: {result} (expected: False)")
    assert result is False, "TrustProfile should block after max_daily"

    print("\n=== All tests passed. Gnowme is ready. ===")

if __name__ == "__main__":
    asyncio.run(test_full_day())
