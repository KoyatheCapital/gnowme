"""
Speech Engine — the voice of Gnowme.

Principles:
  - Sounds like internal thought, NOT instruction
  - Never assumes ("you seem stressed")
  - Never validates weakness ("it's okay to feel…")
  - Always guides toward stability and control
  - Speaks as neutral internal awareness — not "you" or "we"
  - Pauses are part of the speech (marked as [pause])

Structure of every interaction:
  1. Soft Entry
  2. Orientation
  3. Regulation
  4. Direction
  5. Action Lock
"""

from typing import Dict, List
import random


# ─── MORNING WAKE SEQUENCE ────────────────────────────────────────────────────

WAKE_STEPS = [
    # Step 1 — Wake Detection (wait for response after)
    {
        "id": "wake_detect",
        "lines": [
            "Hey…",
            "hello…",
            "are we up yet?"
        ],
        "wait_for_response": True,
    },
    # Step 2 — Engagement
    {
        "id": "engagement",
        "lines": [
            "Alright… good…",
            "take a second… let everything come online…",
            "no rush… just get fully here."
        ],
        "wait_for_response": False,
    },
    # Step 3 — Awareness Check
    {
        "id": "awareness",
        "lines": [
            "Body feels a little slow…",
            "that's fine… we don't need full energy yet…",
            "just presence first."
        ],
        "wait_for_response": False,
    },
    # Step 4 — Regulation
    {
        "id": "regulation",
        "lines": [
            "Take one breath in…",
            "slow…",
            "long exhale…",
            "again… slower on the way out…"
        ],
        "wait_for_response": False,
    },
    # Step 5 — Direction
    {
        "id": "direction",
        "lines": [
            "Today isn't about doing everything…",
            "just moving one thing forward cleanly…",
            "start simple… sit up…",
            "feet on the ground…"
        ],
        "wait_for_response": False,
    },
    # Step 6 — Action Lock
    {
        "id": "action_lock",
        "lines": [
            "Good…",
            "now stand…",
            "we're moving."
        ],
        "wait_for_response": False,
    },
]


# ─── SPEECH SCRIPTS BY MODE ───────────────────────────────────────────────────

SCRIPTS = {

    "midday_intervention": [
        "…hold for a second…\n\neverything is moving fast right now…\nslow the pace just slightly…\n\nnothing needs to be forced…\njust one clear step…\n\nstay centered… then continue.",
        "…pause…\n\nthis is getting loud…\nbut loud doesn't mean urgent…\n\ndrop the speed by half…\nchoose the next right thing only…\n\nthen move.",
    ],

    "decision_moment": [
        "Pause…\n\nthis moment matters…\n\ndon't rush this…\n\nlook at it cleanly…\nwhat actually moves things forward here?\n\n…that's the direction.",
        "…slow down here…\n\nnot everything is as urgent as it feels…\n\nwhat is the one thing that actually matters in this?…\n\ngo with that.",
    ],

    "stress_regulation": [
        "…everything is still manageable…\n\nthe pace picked up…\nthat's all this is…\n\none breath…\nlong exhale…\n\nthen the next step only.",
        "…hold…\n\nstress is information… not instruction…\n\nwhat does the situation actually need right now?\n\nstart there.",
    ],

    "focus_reset": [
        "…scattered right now…\n\nthat's the signal… not the problem…\n\nclose everything that isn't the one thing…\n\nnarrow the target…\nthen begin.",
        "Too many open loops…\n\npick one…\nclose it…\nthe rest can wait.",
    ],

    "low_energy_recovery": [
        "Energy is lower right now…\n\nthat's not a problem to solve…\njust a pace to match…\n\nsmaller steps…\nless force…\nstill moving.",
        "…body needs less input and more output right now…\n\nkeep it simple…\ndon't add to the load…\njust finish one thing.",
    ],

    "negotiation_prep": [
        "…this matters…\n\ndon't enter it rushed…\n\nthe composure before the room…\nthat's the advantage…\n\neverything is already prepared…\njust stay present.",
        "The strategist enters calm…\n\nnot because there's nothing at stake…\nbut because everything at stake requires clarity…\n\nbreathe… then proceed.",
    ],

    "evening_close": [
        "Day is closing…\n\nnothing left to solve right now…\n\nlet everything settle…\n\ntomorrow will organize itself…\n\njust release it… slowly…",
        "…the work is done for today…\n\nwhat happened is already complete…\n\nwhat didn't happen is already let go…\n\nnothing left to carry into the night.",
    ],

    "morning_intention": [
        "Before the noise comes in…\n\none thing…\n\nwhat is the single thing that would make today count?\n\nname it now…\nhold it…\nthat's the north star.",
        "…the day is already forming…\n\ndirect it before it directs you…\n\none clear intention…\nset it now.",
    ],

    "recovery": [
        "…rest is not the absence of work…\n\nit is part of it…\n\nnothing needs to be solved in this moment…\n\nlet the system recover…\nthen continue.",
    ],

    "baseline": [
        "…steady right now…\n\nkeep the pace…\none step at a time…\nstay in it.",
        "…nothing to fix…\njust stay present…\nmoving is enough.",
    ],
}


# ─── BOOK-SPECIFIC GUIDANCE ───────────────────────────────────────────────────

BOOK_GUIDANCE = {
    "rich_dad_poor_dad": {
        "decision": "…before this choice…\n\nis this working for us… or are we working for it?\n\nthat's the only question that matters here.",
        "stress": "…financial pressure is a signal…\nnot a sentence…\n\nwhat asset does this moment reveal?\n\nlook for that.",
        "morning": "…waking as someone who makes things work…\nnot someone things happen to…\n\nthat distinction is already the advantage.",
    },
    "art_of_war": {
        "decision": "…the best outcome often requires no conflict at all…\n\nwhat does the situation actually need?\n\nread it before reacting.",
        "stress": "…composure under pressure is not passive…\nit is the sharpest tool available…\n\nuse it.",
        "morning": "…the strategist sees the board before moving any piece…\n\nwhat does today actually require?\n\nbegin from that.",
    },
    "atomic_habits": {
        "decision": "…what would the person becoming do here?\n\nnot the person who was…\nthe one who is…\n\nthat's the vote.",
        "stress": "…systems over force…\nthe habit doesn't need energy to sustain…\nit just needs continuation…\n\nkeep going.",
        "morning": "…one small thing done with intention…\nthat's the whole architecture…\n\nwhat's the first one?",
    },
    "meditations": {
        "decision": "…what here is actually within control?\n\nonly that…\n\nthe rest is already decided by forces outside this moment.",
        "stress": "…the inner citadel is not affected by outside movement…\n\nreturn to it…\nthen act from there.",
        "morning": "…the emperor rose not because it was easy…\nbut because there was work…\n\nthat is still the reason.",
    },
    "power_of_now": {
        "decision": "…past and future are thoughts…\nthis moment is real…\n\nwhat does this moment actually require?\n\nonly that.",
        "stress": "…the anxiety is about what hasn't happened yet…\nnot what is happening…\n\ncome back…\njust this…\njust now.",
        "morning": "…before any thought of what needs doing…\nthis breath…\n\nalready here…\nalready enough to begin from.",
    },
}


# ─── DECISION INTEGRITY ───────────────────────────────────────────────────────

INTEGRITY_CHECKS = {
    "high_stress": "…not the moment for a major decision…\n\nstress narrows the lens…\n\nif it can wait… let it wait…\nif it can't… keep the scope small.",
    "low_energy": "…low energy shifts risk tolerance…\n\nnothing permanent when the system is depleted…\n\nsmall reversible steps only.",
    "impulsive": "…the speed of this urge is itself the signal…\n\nslow it down…\n\nwhat is this decision actually about?\n\nfind that first.",
}


# ─── COMPOSER ────────────────────────────────────────────────────────────────

def compose(state: Dict, intent: Dict, active_books: List[str], mode: str = None) -> str:
    """
    Compose speech from state + intent + active books.
    Returns a script string with natural pause markers.
    """
    selected_mode = mode or intent.get("mode", "work")
    priority = intent.get("priority", "performance")

    # Decision integrity gate
    if selected_mode == "negotiation" and state.get("stress") == "high":
        parts = [INTEGRITY_CHECKS["high_stress"]]
    elif state.get("energy") == "low" and selected_mode != "recovery":
        parts = [INTEGRITY_CHECKS["low_energy"]]
    else:
        # Base script
        script_pool = SCRIPTS.get(
            f"{state.get('state', 'baseline').replace('acute_pressure', 'stress_regulation').replace('elevated_activation', 'focus_reset').replace('low_energy', 'low_energy_recovery')}",
            SCRIPTS["baseline"]
        )
        parts = [random.choice(script_pool)]

    # Layer in book consciousness (one book, relevant to mode)
    for book in active_books[:1]:
        if book in BOOK_GUIDANCE:
            key = "decision" if selected_mode in ["negotiation", "work"] else "stress" if priority == "calm" else "morning"
            parts.append(BOOK_GUIDANCE[book].get(key, ""))

    return "\n\n".join(p for p in parts if p).strip()


def get_wake_step(step_index: int) -> Dict:
    if step_index < len(WAKE_STEPS):
        return WAKE_STEPS[step_index]
    return {"id": "done", "lines": [], "wait_for_response": False}


def format_for_tts(script: str) -> str:
    """Convert pause markers and ellipses to TTS-friendly format."""
    return script.replace("…", "... ").replace("\n\n", ". ")
