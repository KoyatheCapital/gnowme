from typing import Dict, Any, Optional
from intelligence.consciousness_translator import ConsciousnessTranslator
from core.cci import ContextualCognitiveInterface
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
    - Learns and adapts to user's natural pace over time
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.translator = ConsciousnessTranslator(user_id)
        self.cci = ContextualCognitiveInterface()
        self.trust = TrustProfile()
        self.state_engine = StateEngine()
        # Learned style adjusts with every interaction
        self.learned_style: Dict[str, float] = {
            "pause_density":       0.7,   # how often ellipses appear
            "directive_strength":  0.5,   # how direct vs open-ended
            "line_length":         1.0,   # multiplier on line count
        }

    async def generate(
        self,
        bio_state: Dict,
        context: Dict,
        user_input: str = "",
        feedback: Optional[Dict] = None,
    ) -> str:
        # Adapt style based on last interaction feedback
        if feedback:
            self._update_learned_style(feedback)

        if not self.trust.can_intervene():
            return "…stepping back…\n\nwill be here when the moment is right."

        cci_entry, consent = self.cci.enter(user_input or "a moment of transition", context)
        if not consent:
            return "…got it…\n\nwe can come back to this when you're ready."

        bio = Biometrics(
            hrv=bio_state.get("hrv"),
            heart_rate=bio_state.get("heart_rate"),
            resting_hr=bio_state.get("resting_hr"),
            sleep_score=bio_state.get("sleep_score"),
        )
        state  = self.state_engine.build_state(bio, context)
        intent = self.state_engine.build_intent(state, context)

        raw_script = speech_engine.compose(
            state=state,
            intent=intent,
            active_books=self.translator.active_books,
            mode=intent.get("mode"),
        )

        # Apply learned style so it feels more like the user's own thinking
        personal_script = self._apply_learned_style(raw_script)

        self.trust.record_intervention()
        return personal_script

    # ── Style Learning ──────────────────────────────────────────────────────

    def _update_learned_style(self, feedback: Dict) -> None:
        """Learn from user response to make future monologues feel more natural."""
        # User interrupted → slow down, add more pause space
        if feedback.get("interrupted"):
            self.learned_style["pause_density"] = min(
                1.0, self.learned_style["pause_density"] + 0.08
            )
        # User followed the guidance → slightly less directive over time
        if feedback.get("followed"):
            self.learned_style["directive_strength"] = max(
                0.2, self.learned_style["directive_strength"] - 0.04
            )
        # User skipped quickly → tighten line count
        if feedback.get("skipped_fast"):
            self.learned_style["line_length"] = max(
                0.6, self.learned_style["line_length"] - 0.1
            )

    def _apply_learned_style(self, text: str) -> str:
        """Shape the script to match the user's preferred internal rhythm."""
        # High pause density → heavier ellipsis spacing
        if self.learned_style["pause_density"] > 0.75:
            text = text.replace(". ", "… ")
        # Low directive strength → soften imperative language slightly
        if self.learned_style["directive_strength"] < 0.35:
            text = (text
                    .replace("do the work", "move toward the work")
                    .replace("get up", "come up"))
        return text

    # ── Named Flows ─────────────────────────────────────────────────────────

    async def morning_flow(self, bio_state: Dict, context: Dict) -> str:
        ctx = {**context, "time_of_day": "morning", "activity": "waking_up"}
        return await self.generate(bio_state, ctx, "starting the day")

    async def real_time_flow(
        self, bio_state: Dict, context: Dict, user_input: str = ""
    ) -> str:
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

    async def handle_conflict_response(
        self, user_id: str, user_choice: str, original_context: Dict
    ) -> str:
        name = user_choice.replace("_", " ")
        return f"…{name}…\n\nthat's the direction…\n\nmoving from there now."

    def get_wake_step(self, step_index: int) -> Dict:
        return speech_engine.get_wake_step(step_index)
