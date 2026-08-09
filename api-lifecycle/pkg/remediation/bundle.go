package remediation

import (
    "crypto/sha256"
    "encoding/hex"
    "encoding/json"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
)

type Bundle struct {
    SchemaVersion string `json:"schema_version"`
    Evidence report.Evidence `json:"evidence"`
    EvidenceFingerprint string `json:"evidence_fingerprint"`
    Priority string `json:"priority"`
    Actions []Action `json:"actions"`
}

type Action struct {
    Order int `json:"order"`
    Action string `json:"action"`
    Why string `json:"why"`
}

func Build(e report.Evidence) (Bundle, error) {
    fingerprint, err := report.Fingerprint(e)
    if err != nil { return Bundle{}, err }
    priority := "normal"
    switch e.Decision {
    case "BLOCKED": priority = "critical"
    case "REVIEW": priority = "high"
    }
    actions := make([]Action, 0, len(e.Remediations))
    for i, remediation := range e.Remediations {
        actions = append(actions, Action{Order: i + 1, Action: remediation, Why: reasonFor(e, remediation)})
    }
    if len(actions) == 0 && e.Decision == "SAFE" {
        actions = append(actions, Action{Order: 1, Action: "continue monitoring before retirement", Why: "retirement evidence is currently within policy"})
    }
    return Bundle{SchemaVersion: "1.0", Evidence: e, EvidenceFingerprint: fingerprint, Priority: priority, Actions: actions}, nil
}

func reasonFor(e report.Evidence, remediation string) string {
    for _, reason := range e.Reasons {
        if remediationMatches(reason, remediation) { return reason }
    }
    return "remediation required by deterministic lifecycle policy"
}

func remediationMatches(reason, remediation string) bool {
    // Stable deterministic matching without fuzzy/LLM behavior.
    switch {
    case reason == "unknown traffic exceeds policy threshold":
        return remediation == "identify and attribute unknown consumers"
    case reason == "replacement endpoint is missing":
        return remediation == "define and validate a replacement endpoint"
    case reason == "replacement endpoint is unhealthy":
        return remediation == "restore replacement health before sunset"
    case reason == "active consumers remain observed":
        return remediation == "complete consumer migration"
    case reason == "migration is incomplete":
        return remediation == "reach 100% verified migration"
    default:
        return false
    }
}

func Fingerprint(b Bundle) (string, error) {
    data, err := json.Marshal(b)
    if err != nil { return "", err }
    sum := sha256.Sum256(data)
    return hex.EncodeToString(sum[:]), nil
}
