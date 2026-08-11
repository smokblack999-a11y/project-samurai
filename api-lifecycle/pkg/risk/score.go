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

// Calculate produces an explainable 100-point score from canonical Evidence.
// Hard shutdown policy remains in audit.Policy; this score is a decision aid,
// not permission to bypass safety gates.
func Calculate(e report.Evidence) Score {
    s := Score{}

    // 25: all known consumers have stopped using the retiring endpoint.
    if e.ConsumerCount > 0 && e.ActiveConsumerCount == 0 {
        s.ConsumerCoverage = 25
    }

    // 25: a concrete, healthy replacement exists.
    if strings.TrimSpace(e.Replacement) != "" && e.ReplacementHealthy {
        s.ReplacementReady = 25
    }

    // 15: observed traffic is sufficiently known.
    if e.UnknownTrafficShare <= maxUnknownTrafficShare {
        s.TrafficHealth = 15
        s.UnknownConsumers = 15
    }

    // 10: migration evidence is complete.
    if e.MigrationCompletion >= 1 {
        s.MigrationEvidence = 10
    }

    // 10: RFC 8594 Sunset is useful policy evidence, never a guarantee.
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
