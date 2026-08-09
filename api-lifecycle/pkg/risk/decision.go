package risk

import "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"

type Policy struct {
    MaxUnknownTrafficShare float64 `json:"max_unknown_traffic_share"`
    RequireReplacement bool `json:"require_replacement"`
    RequireHealthyReplacement bool `json:"require_healthy_replacement"`
}

var DefaultPolicy = Policy{MaxUnknownTrafficShare: 0.01, RequireReplacement: true, RequireHealthyReplacement: true}

func Decide(e lifecycle.Endpoint, unknownShare float64, policy Policy) lifecycle.RiskResult {
    reasons := []string{}
    remediations := []string{}
    score := 100
    decision := lifecycle.DecisionSafe
    if unknownShare > policy.MaxUnknownTrafficShare {
        decision = lifecycle.DecisionBlocked
        score -= 60
        reasons = append(reasons, "unknown traffic exceeds policy threshold")
        remediations = append(remediations, "identify and attribute unknown consumers")
    }
    if policy.RequireReplacement && e.Replacement == "" {
        decision = lifecycle.DecisionBlocked
        score -= 25
        reasons = append(reasons, "replacement endpoint is missing")
        remediations = append(remediations, "define and validate a replacement endpoint")
    }
    if policy.RequireHealthyReplacement && !e.ReplacementHealthy {
        decision = lifecycle.DecisionBlocked
        score -= 15
        reasons = append(reasons, "replacement endpoint is unhealthy")
        remediations = append(remediations, "restore replacement health before sunset")
    }
    if e.ActiveConsumerCount > 0 && decision == lifecycle.DecisionSafe {
        decision = lifecycle.DecisionReview
        score -= 20
        reasons = append(reasons, "active consumers remain observed")
        remediations = append(remediations, "complete consumer migration")
    }
    if e.MigrationCompletion < 1 && decision != lifecycle.DecisionBlocked {
        decision = lifecycle.DecisionReview
        score -= 20
        reasons = append(reasons, "migration is incomplete")
        remediations = append(remediations, "reach 100% verified migration")
    }
    if score < 0 { score = 0 }
    confidence := 100
    if unknownShare > 0 { confidence -= 20 }
    if confidence < 0 { confidence = 0 }
    return lifecycle.RiskResult{Decision: decision, Score: score, Confidence: confidence, Reasons: reasons, Remediations: remediations}
}
