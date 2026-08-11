package risk

import (
    "strings"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
)

type Score struct {
    ConsumerCoverage  int `json:"consumer_coverage"`
    ReplacementReady  int `json:"replacement_ready"`
    TrafficHealth     int `json:"traffic_health"`
    UnknownConsumers  int `json:"unknown_consumers"`
    MigrationEvidence int `json:"migration_evidence"`
    SunsetPolicy      int `json:"sunset_policy"`
    Total             int `json:"total"`
    Decision          string `json:"decision"`
}

const maxUnknownTrafficShare = 0.01

// Calculate produces an explainable score from the canonical Evidence model.
// Hard shutdown policy remains in audit.Policy; this score is a decision aid,
// not a permission to bypass safety gates.
func Calculate(e report.Evidence) Score {
    s := Score{}

    // Full consumer coverage is only credited when there are no active callers.
    if e.ConsumerCount > 0 && e.ActiveConsumerCount == 0 {
        s.ConsumerCoverage = 30
    }

    if strings.TrimSpace(e.Replacement) != "" && e.ReplacementHealthy {
        s.ReplacementReady = 25
    }

    if e.UnknownTrafficShare <= maxUnknownTrafficShare {
        s.TrafficHealth = 20
        s.UnknownConsumers = 15
    }

    if e.MigrationCompletion >= 1 {
        s.MigrationEvidence = 10
    }

    // RFC 8594 Sunset is a signal, not a guarantee. Presence earns policy
    // evidence but never overrides runtime consumer or migration evidence.
    if e.Sunset != nil {
        s.SunsetPolicy = 10
    }

    s.Total = s.ConsumerCoverage + s.ReplacementReady + s.TrafficHealth +
        s.UnknownConsumers + s.MigrationEvidence + s.SunsetPolicy

    switch {
    case s.Total >= 85:
        s.Decision = "SAFE"
    case s.Total >= 50:
        s.Decision = "REVIEW"
    default:
        s.Decision = "BLOCKED"
    }
    return s
}
