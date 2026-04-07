from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class Biometrics:
    hrv: float | None = None
    heart_rate: float | None = None
    resting_hr: float | None = None
    sleep_score: float | None = None

class StateEngine:
    def build_state(self, bio: Biometrics, context: Dict) -> Dict:
        features = self._extract_features(bio)
        state, intensity = self._classify(features, context)
        confidence = self._compute_confidence(features, context)

        return {
            "state": state,
            "intensity": round(intensity, 2),
            "confidence": round(confidence, 2),
            "features": features,
            "use_soft_language": confidence < 0.70,
            "recommended_tone": "soft" if confidence < 0.70 else "grounded"
        }

    def _extract_features(self, bio: Biometrics) -> Dict:
        features = {}
        if bio.hrv is not None and bio.hrv < 45:
            features["low_hrv"] = True
        if bio.heart_rate is not None and bio.resting_hr is not None and bio.heart_rate > bio.resting_hr + 25:
            features["hr_spike"] = True
        if bio.sleep_score is not None and bio.sleep_score < 65:
            features["low_recovery"] = True
        return features

    def _classify(self, features: Dict, context: Dict) -> Tuple[str, float]:
        if features.get("hr_spike") and features.get("low_hrv"):
            return "acute_pressure", 0.90
        if features.get("low_hrv"):
            return "elevated_activation", 0.75
        if features.get("low_recovery"):
            return "low_energy", 0.80
        return "baseline", 0.50

    def _compute_confidence(self, features: Dict, context: Dict) -> float:
        base = 0.55
        if len(features) >= 2:
            base += 0.25
        if context.get("agent_context"):
            base += 0.10
        return min(base, 0.95)
