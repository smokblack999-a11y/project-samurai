package risk

import "github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/model"

type Engine struct{}

func New() Engine { return Engine{} }

func (Engine) Evaluate(r model.LifecycleRecord) model.RiskDecision {
	score := 0
	reasons := make([]string, 0, 6)
	if r.ActiveConsumerCount > 0 { score += 40; reasons = append(reasons, "active_consumers") }
	if r.TrafficShare >= 0.10 { score += 25; reasons = append(reasons, "high_traffic") } else if r.TrafficShare > 0 { score += 10 }
	if r.UnknownTrafficShare >= 0.05 { score += 20; reasons = append(reasons, "unknown_traffic") }
	if r.MigrationCompletion < 1 { score += 20; reasons = append(reasons, "migration_incomplete") }
	if r.Replacement != "" && !r.ReplacementHealthy { score += 15; reasons = append(reasons, "replacement_unhealthy") }
	if r.Status == model.StatusActive { return model.RiskDecision{Decision:model.RiskSafe, Score:0, Reasons:[]string{"not_deprecated"}} }
	level := model.RiskSafe
	if score >= 50 { level = model.RiskBlocked } else if score >= 20 { level = model.RiskReview }
	return model.RiskDecision{Decision:level, Score:score, Reasons:reasons}
}
