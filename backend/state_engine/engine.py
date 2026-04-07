from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class Biometrics:
    hrv: float | None = None
    heart_rate: float | None = None
    resting_hr: float | None = None
    sleep_score: float | None = None
    body_temp_delta: float | None = None  # deviation from personal baseline

class StateEngine:
    """
    Sense → Understand → Decide
    Outputs energy / stress / focus / readiness — not emotion labels.
    """

    def build_state(self, bio: Biometrics, context: Dict) -> Dict:
        features = self._extract_features(bio)
        energy   = self._score_energy(features)
        stress   = self._score_stress(features)
        focus    = self._score_focus(features)
        readiness = self._score_readiness(energy, stress, focus)
        confidence = self._compute_confidence(features, context)

        return {
            "energy":    energy,
            "stress":    stress,
            "focus":     focus,
            "readiness": readiness,
            "confidence": round(confidence, 2),
            "features":  features,
            "use_soft_language": confidence < 0.70,
            "recommended_tone": "soft" if confidence < 0.70 else "grounded",
            # legacy compat
            "state":     self._legacy_state(energy, stress),
            "intensity": 0.75,
        }

    def build_intent(self, state: Dict, context: Dict) -> Dict:
        time     = context.get("time_of_day", "day")
        activity = context.get("activity", "general")

        if time == "morning" or activity == "waking_up":
            mode = "wake"
        elif state["stress"] == "high" or activity in ["negotiation", "meeting"]:
            mode = "negotiation"
        elif state["energy"] == "low":
            mode = "recovery"
        else:
            mode = "work"

        if state["stress"] == "high":
            priority = "calm"
        elif state["focus"] == "scattered":
            priority = "clarity"
        else:
            priority = "performance"

        return {"mode": mode, "priority": priority}

    def _extract_features(self, bio: Biometrics) -> Dict:
        f = {}
        if bio.hrv is not None:
            if bio.hrv < 35:   f["hrv_critical"] = True
            elif bio.hrv < 45: f["low_hrv"] = True
        if bio.heart_rate is not None and bio.resting_hr is not None:
            delta = bio.heart_rate - bio.resting_hr
            if delta > 30:   f["hr_spike"] = True
            elif delta > 15: f["hr_elevated"] = True
        if bio.sleep_score is not None:
            if bio.sleep_score < 55:   f["poor_sleep"] = True
            elif bio.sleep_score < 70: f["low_recovery"] = True
        if bio.body_temp_delta is not None and abs(bio.body_temp_delta) > 0.5:
            f["temp_deviation"] = True
        return f

    def _score_energy(self, features: Dict) -> str:
        if features.get("poor_sleep") or features.get("hrv_critical"):   return "low"
        if features.get("low_recovery") or features.get("low_hrv"):      return "medium"
        return "high"

    def _score_stress(self, features: Dict) -> str:
        if features.get("hr_spike") and features.get("low_hrv"):   return "high"
        if features.get("hr_elevated") or features.get("hrv_critical"): return "elevated"
        return "low"

    def _score_focus(self, features: Dict) -> str:
        if features.get("poor_sleep") and features.get("hr_spike"): return "scattered"
        if features.get("low_recovery"):                             return "stable"
        return "deep"

    def _score_readiness(self, energy: str, stress: str, focus: str) -> str:
        score  = {"low": 0, "medium": 1, "high": 2}[energy]
        score += {"high": 0, "elevated": 1, "low": 2}[stress]
        score += {"scattered": 0, "stable": 1, "deep": 2}[focus]
        if score >= 5: return "peak"
        if score >= 3: return "ready"
        return "low"

    def _compute_confidence(self, features: Dict, context: Dict) -> float:
        base = 0.55
        if len(features) >= 2:         base += 0.25
        if context.get("agent_context"): base += 0.10
        return min(base, 0.95)

    def _legacy_state(self, energy: str, stress: str) -> str:
        if stress == "high":     return "acute_pressure"
        if stress == "elevated": return "elevated_activation"
        if energy == "low":      return "low_energy"
        return "baseline"
