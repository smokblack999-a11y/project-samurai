package remediation

import (
    "crypto/sha256"
    "encoding/hex"
    "encoding/json"
    "strings"

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
    actions := make([]Action, 0, len(e.Reasons))
    for i, reason := range e.Reasons {
        action := actionFor(reason)
        if action == "" { action = "investigate lifecycle evidence" }
        actions = append(actions, Action{Order: i + 1, Action: action, Why: reason})
    }
    if len(actions) == 0 && e.Decision == "SAFE" {
        actions = append(actions, Action{Order: 1, Action: "continue monitoring before retirement", Why: "retirement evidence is currently within policy"})
    }
    return Bundle{SchemaVersion: "1.0", Evidence: e, EvidenceFingerprint: fingerprint, Priority: priority, Actions: actions}, nil
}

func actionFor(reason string) string {
    switch {
    case strings.Contains(reason, "unknown traffic"):
        return "identify and attribute unknown consumers"
    case strings.Contains(reason, "replacement endpoint is missing"):
        return "define and validate a replacement endpoint"
    case strings.Contains(reason, "replacement endpoint is not healthy") || strings.Contains(reason, "replacement endpoint is unhealthy"):
        return "restore replacement health before sunset"
    case strings.Contains(reason, "active consumers"):
        return "complete consumer migration"
    case strings.Contains(reason, "migration is incomplete"):
        return "reach 100% verified migration"
    default:
        return ""
    }
}

func Fingerprint(b Bundle) (string, error) {
    data, err := json.Marshal(b)
    if err != nil { return "", err }
    sum := sha256.Sum256(data)
    return hex.EncodeToString(sum[:]), nil
}
