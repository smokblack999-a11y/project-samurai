package audit

import (
    "strings"
    "time"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/consumer"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/risk"
)

type Input struct {
    Endpoint lifecycle.Endpoint
    Records []consumer.AccessRecord
    Sunset *time.Time
    Replacement string
    ReplacementHealthy bool
    MigrationCompletion float64
    Policy risk.Policy
}

func Run(in Input) report.Evidence {
    a := consumer.Attribute(in.Endpoint, in.Records)
    reasons := make([]string, 0, 4)
    decision := "SAFE"

    if a.UnknownTrafficShare > in.Policy.MaxUnknownTrafficShare {
        decision = "BLOCKED"
        reasons = append(reasons, "unknown traffic exceeds policy threshold")
    }
    if in.Policy.RequireReplacement && strings.TrimSpace(in.Replacement) == "" {
        decision = "BLOCKED"
        reasons = append(reasons, "replacement endpoint is missing")
    }
    if in.Policy.RequireHealthyReplacement && !in.ReplacementHealthy {
        decision = "BLOCKED"
        reasons = append(reasons, "replacement endpoint is not healthy")
    }
    if in.MigrationCompletion < 1 {
        if decision != "BLOCKED" { decision = "REVIEW" }
        reasons = append(reasons, "consumer migration is incomplete")
    }
    if a.ActiveConsumerCount > 0 && decision == "SAFE" {
        decision = "REVIEW"
        reasons = append(reasons, "active consumers remain observed")
    }

    return report.Evidence{
        GeneratedAt: time.Now().UTC(),
        Endpoint: in.Endpoint.Endpoint,
        Method: in.Endpoint.Method,
        Sunset: in.Sunset,
        Replacement: in.Replacement,
        ConsumerCount: a.ConsumerCount,
        ActiveConsumerCount: a.ActiveConsumerCount,
        UnknownTrafficShare: a.UnknownTrafficShare,
        MigrationCompletion: in.MigrationCompletion,
        ReplacementHealthy: in.ReplacementHealthy,
        Decision: decision,
        Reasons: reasons,
    }
}
