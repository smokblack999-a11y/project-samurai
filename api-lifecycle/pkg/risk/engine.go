package risk

import (
	"fmt"
	"math"

	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

// Evaluate is deterministic. AI may explain or enrich a decision later,
// but the shutdown gate remains reproducible and auditable.
func Evaluate(e lifecycle.Endpoint) lifecycle.RiskResult {
	score := 0
	reasons := make([]string, 0, 8)
	remediations := make([]string, 0, 8)

	if e.Status != lifecycle.StatusSunset {
		reasons = append(reasons, "endpoint is not explicitly marked for sunset")
		remediations = append(remediations, "mark the endpoint for sunset only after the deprecation process is complete")
	}
	if e.Status == lifecycle.StatusSunset && e.Sunset.IsZero() {
		reasons = append(reasons, "sunset status has no sunset timestamp")
		remediations = append(remediations, "set an explicit sunset timestamp")
	}

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

	if e.Replacement != "" {
		if e.MigrationCompletion < 1 {
			points := int(math.Ceil((1 - clamp01(e.MigrationCompletion)) * 30))
			score += min(30, points)
			reasons = append(reasons, fmt.Sprintf("migration to %s is %.0f%% complete", e.Replacement, clamp01(e.MigrationCompletion)*100))
			remediations = append(remediations, "complete or explicitly waive migration")
		}
		if !e.ReplacementHealthy {
			score += 25
			reasons = append(reasons, "replacement endpoint is not healthy")
			remediations = append(remediations, "restore replacement health before sunset")
		}
	}

	if score > 100 {
		score = 100
	}

	decision := lifecycle.DecisionSafe
	switch {
	case e.Status != lifecycle.StatusSunset:
		decision = lifecycle.DecisionBlocked
	case e.Sunset.IsZero():
		decision = lifecycle.DecisionBlocked
	case e.ActiveConsumerCount > 0:
		decision = lifecycle.DecisionBlocked
	case e.UnknownTrafficShare > 0.01:
		decision = lifecycle.DecisionBlocked
	case e.Replacement != "" && !e.ReplacementHealthy:
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
		Decision: decision,
		Score: score,
		Confidence: confidence,
		Reasons: reasons,
		Remediations: remediations,
	}
}

func clamp01(v float64) float64 {
	if v < 0 {
		return 0
	}
	if v > 1 {
		return 1
	}
	return v
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
