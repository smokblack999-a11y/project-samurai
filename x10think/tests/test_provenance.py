from provenance import proposal_fingerprint


def test_same_inputs_have_same_fingerprint():
    proposal = {"severity": "low", "recommended_action": "health"}
    source = {"host": "demo", "score": 0.98}
    assert proposal_fingerprint(proposal, source) == proposal_fingerprint(proposal, source)


def test_changed_source_changes_fingerprint():
    proposal = {"severity": "low", "recommended_action": "health"}
    source = {"host": "demo", "score": 0.98}
    assert proposal_fingerprint(proposal, source) != proposal_fingerprint(proposal, {**source, "score": 0.70})
