from typing import Dict

REFRAMES: Dict[str, Dict[str, str]] = {
    "dichotomy_of_control": {
        "acute_pressure": "What you cannot control is already gone. What you can control is right here, right now.",
        "elevated_activation": "The pressure you feel is energy. Direct it toward what is within your reach.",
        "low_energy": "Rest is not retreat. Recovery is part of the work.",
        "baseline": "Stay present. The next right action is enough."
    },
    "memento_mori": {
        "acute_pressure": "This moment, like all moments, will pass. Act with clarity while it's here.",
        "elevated_activation": "What truly matters today? Let that guide your next step.",
        "low_energy": "Even Marcus Aurelius had days where rising was hard. You're still here.",
        "baseline": "Each day is a chance to act with purpose. Use it well."
    }
}

def get_stoic_reframe(principle: str, human_state: str) -> str:
    principle_map = REFRAMES.get(principle, REFRAMES["dichotomy_of_control"])
    return principle_map.get(human_state, principle_map["baseline"])
