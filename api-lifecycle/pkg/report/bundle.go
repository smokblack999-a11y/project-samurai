package report

import "time"

type EvidenceBundle struct {
    GeneratedAt time.Time `json:"generated_at"`
    EvidenceFingerprint string `json:"evidence_fingerprint"`
    Evidence Evidence `json:"evidence"`
    Priority string `json:"priority"`
    Actions []RemediationAction `json:"actions"`
}

type RemediationAction struct {
    Order int `json:"order"`
    Action string `json:"action"`
    Reason string `json:"reason"`
    Blocking bool `json:"blocking"`
}

func BuildBundle(e Evidence) (EvidenceBundle, error) {
    fp, err := Fingerprint(e)
    if err != nil { return EvidenceBundle{}, err }
    priority := "low"
    if e.Decision == "REVIEW" { priority = "medium" }
    if e.Decision == "BLOCKED" { priority = "high" }
    actions := make([]RemediationAction, 0, len(e.Remediations))
    for i, remediation := range e.Remediations {
        actions = append(actions, RemediationAction{Order: i + 1, Action: remediation, Reason: "deterministic audit remediation", Blocking: e.Decision == "BLOCKED"})
    }
    return EvidenceBundle{GeneratedAt: time.Now().UTC(), EvidenceFingerprint: fp, Evidence: e, Priority: priority, Actions: actions}, nil
}
