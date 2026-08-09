package remediation

import (
    "testing"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
)

func TestBuildBlockedBundle(t *testing.T) {
    e := report.Evidence{
        Endpoint: "/v1/orders", Method: "GET", Decision: "BLOCKED", Score: 25, Confidence: 80,
        AffectedConsumers: []string{"billing", "legacy-worker"},
        Reasons: []string{"unknown traffic exceeds policy threshold", "replacement endpoint is missing"},
        Remediations: []string{"identify and attribute unknown consumers", "define and validate a replacement endpoint"},
    }
    b, err := Build(e)
    if err != nil { t.Fatal(err) }
    if b.Priority != "critical" { t.Fatalf("priority=%q", b.Priority) }
    if len(b.Actions) != 2 { t.Fatalf("actions=%d", len(b.Actions)) }
    if b.EvidenceFingerprint == "" { t.Fatal("missing evidence fingerprint") }
    if b.Actions[0].Why == "" { t.Fatal("missing action rationale") }
}

func TestBuildSafeBundle(t *testing.T) {
    e := report.Evidence{Endpoint: "/v1/orders", Method: "GET", Decision: "SAFE", Score: 100, Confidence: 100}
    b, err := Build(e)
    if err != nil { t.Fatal(err) }
    if b.Priority != "normal" { t.Fatalf("priority=%q", b.Priority) }
    if len(b.Actions) != 1 { t.Fatalf("actions=%d", len(b.Actions)) }
}
