package githubremediation

import (
    "testing"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
)

func TestBuildIssueActionSafeCloses(t *testing.T) {
    e := report.Evidence{Endpoint:"/v1/orders", Method:"GET", Decision:"SAFE", Score:95, Confidence:95}
    a, err := BuildIssueAction(e); if err != nil { t.Fatal(err) }
    if !a.Close { t.Fatal("SAFE must resolve remediation") }
    if a.Fingerprint == "" { t.Fatal("missing fingerprint") }
}

func TestBuildIssueActionBlockedStaysOpen(t *testing.T) {
    e := report.Evidence{Endpoint:"/v1/orders", Method:"GET", Decision:"BLOCKED", Score:20, Confidence:90, Reasons:[]string{"active consumer"}}
    a, err := BuildIssueAction(e); if err != nil { t.Fatal(err) }
    if a.Close { t.Fatal("BLOCKED must remain open") }
}
