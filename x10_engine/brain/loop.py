from .critic import attack
from .decision import Opportunity, evaluate
from .hypothesis import Hypothesis


def run_cycle(h: Hypothesis, scores: Opportunity) -> dict:
    """Deterministic decision loop; it does not claim that research happened."""
    evidence_status = h.classify()
    critique = attack({**scores.normalized(), "access": scores.access, "speed": 100 - scores.speed})
    decision = evaluate(scores)

    # Evidence gate: no GO without actual evidence in the hypothesis record.
    if evidence_status != "SUPPORTED" and decision["decision"] == "GO":
        decision = {**decision, "decision": "REWORK", "next_move": "collect evidence before building"}

    return {
        "hypothesis": h.falsification_plan(),
        "hypothesis_status": evidence_status,
        "critique": {
            "kill_score": critique.kill_score,
            "reasons": critique.reasons,
            "mandatory_tests": critique.mandatory_tests,
        },
        "decision": decision,
    }
