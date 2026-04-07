from typing import Dict, Tuple
import random

class ContextualCognitiveInterface:
    """Respectful human entry before any guidance."""

    def __init__(self):
        self.mirrors = [
            "You're feeling {emotion} right now.",
            "It sounds like {situation} is present."
        ]
        self.validations = [
            "That makes sense given what you're carrying.",
            "Anyone would feel that way right now."
        ]
        self.permissions = [
            "Do you have {time} seconds to reset together?",
            "Is this a good moment for a short breath?"
        ]

    def enter(self, user_input: str, context: Dict) -> Tuple[str, bool]:
        emotion = self._extract_emotion(user_input)
        mirror = random.choice(self.mirrors).format(emotion=emotion, situation=user_input[:60])
        validation = random.choice(self.validations)

        time_str = "20" if context.get("availability", "micro") == "micro" else "60"
        permission = random.choice(self.permissions).format(time=time_str)

        entry = f"{mirror} {validation} {permission} This will take about {time_str} seconds."
        consent = True  # In real app: voice yes/no
        return entry, consent

    def _extract_emotion(self, text: str) -> str:
        lower = text.lower()
        if any(w in lower for w in ["stressed", "anxious", "pressure"]):
            return "pressure rising"
        if any(w in lower for w in ["tired", "low", "fatigue"]):
            return "energy is lower"
        return "a moment of transition"
