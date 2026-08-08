package risk

import "github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/model"

type Engine struct { thresholds Thresholds }

func New() Engine { return Engine{thresholds: DefaultThresholds} }

func (e Engine) Evaluate(r model.LifecycleRecord) model.RiskDecision {
	score := 0
	reasons := make([]string, 0, 6)
	evidence := map[string]any{
		"active_consumers":       r.ActiveConsumerCount,
		"consumer_count":        r.ConsumerCount,
		"traffic_share":         r.TrafficShare,
		"unknown_traffic_share": r.UnknownTrafficShare,
		"migration_completion":  r.MigrationCompletion,
		"replacement_healthy":   r.ReplacementHealthy,
	}

	if r.ActiveConsumerCount > 0 { score += 40; reasons = append(reasons, "active_consumers") }
	if r.TrafficShare >= e.thresholds.HighTrafficShare { score += 25; reasons = append(reasons, "high_traffic") }
	if r.UnknownTrafficShare >= e.thresholds.HighUnknownShare { score += 15; reasons = append(reasons, "unknown_traffic") }
	if r.MigrationCompletion < e.thresholds.CompleteMigration { score += 15; reasons = append(reasons, "migration_incomplete") }
	if r.Replacement != "" && !r.ReplacementHealthy { score += 20; reasons = append(reasons, "replacement_unhealthy") }

	decision := model.DecisionSafe
	if r.ActiveConsumerCount > 0 || r.MigrationCompletion < e.thresholds.CompleteMigration {
		decision = model.DecisionBlocked
	} else if score >= 30 {
		decision = model.DecisionReview
	}

	return model.RiskDecision{Decision: decision, Score: score, Reasons: reasons, Evidence: evidence}
}
