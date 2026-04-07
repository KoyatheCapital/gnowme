from typing import Dict, Any
from intelligence.consciousness_translator import ConsciousnessTranslator
from core.cci import ContextualCognitiveInterface
from trust.controller import TrustProfile
from state_engine.engine import StateEngine, Biometrics

class InternalMonologueGenerator:
    """
    Generates natural, flowing internal monologues in the user's cloned voice.
    Strictly human-mindset focused. Handles book conflicts gracefully.
    """

    def __init__(self, user_id: str):
        self.translator = ConsciousnessTranslator(user_id)
        self.cci = ContextualCognitiveInterface()
        self.trust = TrustProfile()
        self.state_engine = StateEngine()

    async def generate(self, bio_state: Dict, context: Dict, user_input: str = "") -> str:
        # 1. Trust & Intervention Budget Check
        if not self.trust.can_intervene():
            return "Stepping back for now… I'll be here when the moment feels right."

        # 2. CCI respectful entry
        cci_entry, consent = self.cci.enter(user_input or "a moment of transition", context)
        if not consent:
            return "Got it. We can come back to this when you're ready."

        # 3. Get human-focused guidance (may return conflict question)
        blended_guidance = self.translator.translate(bio_state, context, user_input)

        # 4. Build natural internal monologue
        parts = [
            cci_entry,
            blended_guidance,
            "Breathe deeper… let the exhale release what you cannot control.",
            "The next step is yours. One steady movement forward is enough."
        ]

        self.trust.record_intervention()
        return "\n".join([p for p in parts if p])

    async def morning_flow(self, bio_state: Dict, context: Dict) -> str:
        context = {**context, "time_of_day": "morning", "activity": "waking_up"}
        return await self.generate(bio_state, context, "starting the day")

    async def real_time_flow(self, bio_state: Dict, context: Dict, user_input: str = "") -> str:
        context = {**context, "agent_context": True}
        return await self.generate(bio_state, context, user_input)

    async def handle_conflict_response(self, user_id: str, user_choice: str, original_context: Dict) -> str:
        """User chose primary consciousness when conflict was detected"""
        readable = user_choice.replace("_", " ").title()
        return (
            f"You chose {readable} as the primary mindset right now. "
            "That's a clear decision. Let's move with that steadiness. "
            "The choice is yours from here."
        )
