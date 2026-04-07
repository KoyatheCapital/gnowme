from typing import Dict, Any
from intelligence.consciousness_translator import ConsciousnessTranslator
from trust.controller import TrustProfile
from state_engine.engine import StateEngine, Biometrics
from core import speech_engine

class InternalMonologueGenerator:
    """
    Sense → Understand → Decide → Speak → Adapt

    Speech rules:
    - Internal voice, not instruction
    - Never assumes state ("you seem…")
    - Never validates weakness ("it's okay to…")
    - Guides toward stability and control
    - Neutral internal awareness
    """

    def __init__(self, user_id: str):
        self.translator = ConsciousnessTranslator(user_id)
        self.trust = TrustProfile()
        self.state_engine = StateEngine()

    async def generate(self, bio_state: Dict, context: Dict, user_input: str = "") -> str:
        if not self.trust.can_intervene():
            return "…stepping back…\n\nwill be here when the moment is right."

        bio = Biometrics(
            hrv=bio_state.get("hrv"),
            heart_rate=bio_state.get("heart_rate"),
            resting_hr=bio_state.get("resting_hr"),
            sleep_score=bio_state.get("sleep_score"),
        )
        state = self.state_engine.build_state(bio, context)
        intent = self.state_engine.build_intent(state, context)

        script = speech_engine.compose(
            state=state,
            intent=intent,
            active_books=self.translator.active_books,
            mode=intent.get("mode"),
        )

        self.trust.record_intervention()
        return script

    async def morning_flow(self, bio_state: Dict, context: Dict) -> str:
        ctx = {**context, "time_of_day": "morning", "activity": "waking_up"}
        return await self.generate(bio_state, ctx, "waking_up")

    async def real_time_flow(self, bio_state: Dict, context: Dict, user_input: str = "") -> str:
        ctx = {**context, "agent_context": True}
        return await self.generate(bio_state, ctx, user_input)

    async def midday(self, bio_state: Dict, context: Dict) -> str:
        import random
        return random.choice(speech_engine.SCRIPTS["midday_intervention"])

    async def decision_moment(self, bio_state: Dict, context: Dict) -> str:
        import random
        return random.choice(speech_engine.SCRIPTS["decision_moment"])

    async def evening(self, bio_state: Dict, context: Dict) -> str:
        import random
        return random.choice(speech_engine.SCRIPTS["evening_close"])

    async def handle_conflict_response(self, user_id: str, user_choice: str, original_context: Dict) -> str:
        name = user_choice.replace("_", " ")
        return f"…{name}…\n\nthat's the direction…\n\nmoving from there now."

    def get_wake_step(self, step_index: int) -> Dict:
        return speech_engine.get_wake_step(step_index)
