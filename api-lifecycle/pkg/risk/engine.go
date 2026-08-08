package risk

import (
	"fmt"
	"math"

	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

// Evaluate is deliberately deterministic. AI may explain or enrich a decision later,
// but the shutdown gate must remain reproducible and auditable.
func Evaluate(e lifecycle.Endpoint) lifecycle.RiskResult {
	var score int
	var reasons []string
	var remediations []string

	if e.ActiveConsumerCount > 0 {
		score += min(35, e.ActiveConsumerCount*7)
		reasons = append(reasons, fmt.Sprintf("%d active consumers remain", e.ActiveConsumerCount))
		remediations = append(remediations, "migrate all active consumers")
	}
	if e.TrafficShare > 0.01 {
		points := int(math.Ceil(e.TrafficShare * 40))
		score += min(40, points)
		reasons = append(reasons, fmt.Sprintf("%.1f%% of observed traffic still targets this endpoint", e.TrafficShare*100))
		remediations = append(remediations, "verify traffic has reached zero or an approved low-risk threshold")
	}
	if e.UnknownTrafficShare > 0.01 {
		points := int(math.Ceil(e.UnknownTrafficShare * 30))
		score += min(30, points)
		reasons = append(reasons, fmt.Sprintf("%.1f%% of traffic is from unknown consumers", e.UnknownTrafficShare*100))
		remediations = append(remediations, "identify unknown consumers before shutdown")
	}
	if e.MigrationCompletion < 1 {
		points := int(math.Ceil((1-e.MigrationCompletion) * 30))
		score += min(30, points)
		reasons = append(reasons, fmt.Sprintf("migration is %.0f%% complete", e.MigrationCompletion*100))
		remediations = append(remediations, "complete or explicitly waive migration")
	}
	if e.Replacement != "" && !e.ReplacementHealthy {
		score += 25
		reasons = append(reasons, "replacement endpoint is not healthy")
		remediations = append(remediations, "restore replacement health before sunset")
	}

	if score > 100 {
		score = 100
	}

	decision := lifecycle.DecisionSafe
	switch {
	case e.Status != lifecycle.StatusSunset:
		decision = lifecycle.DecisionBlocked
		reasons = append(reasons, "endpoint is not explicitly marked for sunset")
	case e.ActiveConsumerCount > 0 || e.UnknownTrafficShare > 0.01 || !e.ReplacementHealthy:
		decision = lifecycle.DecisionBlocked
	case score >= 20:
		decision = lifecycle.DecisionReview
	}

	confidence := 100 - score
	if e.UnknownTrafficShare > 0.01 {
		confidence -= 15
	}
	if confidence < 0 {
		confidence = 0
	}

	return lifecycle.RiskResult{
		Decision: lifecycle.Decision(decision),
		Score: score,
		Confidence: confidence,
		Reasons: reasons,
		Remediations: remediations,
	}
}

func min(a, b int) int {
	if a < b { return a }
	return b
}
