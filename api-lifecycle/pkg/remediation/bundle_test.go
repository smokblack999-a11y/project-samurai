package remediation

import "testing"

func TestBuildBlockedBundle(t *testing.T) {
    e := testEvidence("BLOCKED", []string{
        "unknown traffic exceeds policy threshold",
        "replacement endpoint is missing",
        "migration is incomplete",
    })
    b, err := Build(e)
    if err != nil { t.Fatal(err) }
    if b.Priority != "critical" { t.Fatalf("priority=%q", b.Priority) }
    if len(b.Actions) != 3 { t.Fatalf("actions=%d", len(b.Actions)) }
    if b.EvidenceFingerprint == "" { t.Fatal("missing evidence fingerprint") }
    if b.Actions[0].Why == "" { t.Fatal("missing action rationale") }
}

func TestBuildSafeBundle(t *testing.T) {
    e := testEvidence("SAFE", nil)
    b, err := Build(e)
    if err != nil { t.Fatal(err) }
    if b.Priority != "normal" { t.Fatalf("priority=%q", b.Priority) }
    if len(b.Actions) != 1 { t.Fatalf("actions=%d", len(b.Actions)) }
}

func TestFingerprintDeterministic(t *testing.T) {
    e := testEvidence("REVIEW", []string{"active consumers remain observed"})
    a, err := Build(e); if err != nil { t.Fatal(err) }
    b, err := Build(e); if err != nil { t.Fatal(err) }
    if a.EvidenceFingerprint != b.EvidenceFingerprint { t.Fatal("fingerprint is not deterministic") }
}
