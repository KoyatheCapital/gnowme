from typing import Dict, Any
from intelligence.consciousness_translator import ConsciousnessTranslator
from core.cci import ContextualCognitiveInterface
from trust.controller import TrustProfile

class InternalMonologueGenerator:
    def __init__(self, user_id: str):
        self.translator = ConsciousnessTranslator(user_id)
        self.cci = ContextualCognitiveInterface()
        self.trust = TrustProfile()

    async def generate(self, bio_state: Dict, context: Dict, user_input: str = "") -> str:
        if not self.trust.can_intervene():
            return "Stepping back for now… I'll be here when the moment feels right."

        cci_entry, consent = self.cci.enter(user_input or "a moment of transition", context)
        if not consent:
            return "Got it. We can come back to this when you're ready."

        blended_guidance = self.translator.translate(bio_state, context, user_input)

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
