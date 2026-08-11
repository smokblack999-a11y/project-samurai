from moneyproof import CommercialEvidence, Decision, MoneyProof, Signal


def test_paid_signal_allows_build():
    proof = MoneyProof(
        buyer="security team",
        pain="unverified findings",
        offer="verification audit",
        price_usd=1000,
        evidence=[CommercialEvidence(Signal.PAID, "invoice", "buyer paid", "paid")],
    )
    assert proof.decide() is Decision.BUILD
    assert proof.score() == 100.0


def test_demo_signal_requires_sell_test():
    evidence = CommercialEvidence(
        Signal.QUALIFIED_DEMO, "crm", "buyer requested demo", "demo booked"
    )
    assert MoneyProof("buyer", "pain", "offer", 500, [evidence]).decide() is Decision.SELL_TEST


def test_speculation_is_killed():
    evidence = CommercialEvidence(
        Signal.SPECULATION, "model", "market seems interested", "no customer evidence"
    )
    assert MoneyProof("buyer", "pain", "offer", 500, [evidence]).decide() is Decision.KILL


def test_no_evidence_is_killed():
    assert MoneyProof("buyer", "pain", "offer", 500).decide() is Decision.KILL
