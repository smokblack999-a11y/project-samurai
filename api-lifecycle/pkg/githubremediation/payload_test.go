package githubremediation

import (
    "strings"
    "testing"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
)

func TestBuildBlockedPayload(t *testing.T) {
    e := report.Evidence{Endpoint:"/v1/orders", Method:"GET", Decision:"BLOCKED", Score:25, Confidence:80, AffectedConsumers:[]string{"legacy-worker","billing"}, Reasons:[]string{"replacement endpoint is missing"}, Remediations:[]string{"define and validate a replacement endpoint"}}
    p, err := Build(e); if err != nil { t.Fatal(err) }
    if p.Decision != "BLOCKED" || p.Fingerprint == "" { t.Fatalf("bad payload: %+v", p) }
    if !strings.Contains(p.Body, "legacy-worker") || !strings.Contains(p.Body, "No automatic destructive") { t.Fatal("missing evidence/safety text") }
}

func TestFingerprintOrderIndependent(t *testing.T) {
    a := report.Evidence{Endpoint:"/x", Method:"GET", Decision:"REVIEW", Score:50, Confidence:70, AffectedConsumers:[]string{"b","a"}, Reasons:[]string{"z","a"}}
    b := a; b.AffectedConsumers=[]string{"a","b"}; b.Reasons=[]string{"a","z"}
    if fingerprint(a) != fingerprint(b) { t.Fatal("fingerprint depends on ordering") }
}
