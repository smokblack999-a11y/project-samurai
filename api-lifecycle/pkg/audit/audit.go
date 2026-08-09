package audit

import (
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
    endpoint := in.Endpoint
    endpoint.Replacement = in.Replacement
    endpoint.ReplacementHealthy = in.ReplacementHealthy
    endpoint.MigrationCompletion = in.MigrationCompletion
    endpoint.ActiveConsumerCount = a.ActiveConsumerCount

    policy := in.Policy
    result := risk.Decide(endpoint, a.UnknownTrafficShare, policy)

    seen := make(map[string]struct{})
    affected := make([]string, 0, len(in.Records))
    for _, r := range in.Records {
        if r.ConsumerID == "" { continue }
        if _, ok := seen[r.ConsumerID]; ok { continue }
        seen[r.ConsumerID] = struct{}{}
        affected = append(affected, r.ConsumerID)
    }

    return report.Evidence{
        GeneratedAt: time.Now().UTC(),
        Endpoint: in.Endpoint.Endpoint,
        Method: in.Endpoint.Method,
        Status: string(in.Endpoint.Status),
        Sunset: in.Sunset,
        Replacement: in.Replacement,
        ConsumerCount: a.ConsumerCount,
        ActiveConsumerCount: a.ActiveConsumerCount,
        UnknownTrafficShare: a.UnknownTrafficShare,
        MigrationCompletion: in.MigrationCompletion,
        ReplacementHealthy: in.ReplacementHealthy,
        AffectedConsumers: affected,
        Decision: string(result.Decision),
        Score: result.Score,
        Confidence: result.Confidence,
        Reasons: result.Reasons,
        Remediations: result.Remediations,
    }
}
