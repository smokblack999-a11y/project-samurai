package risk

import (
 "github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/model"
)

func Evaluate(r model.LifecycleRecord) model.DecisionResult {
 score := 0
 reasons := make([]string, 0, 6)
 if r.ActiveConsumerCount > 0 { score += 40; reasons = append(reasons, "active_consumers") }
 if r.TrafficShare >= 0.10 { score += 25; reasons = append(reasons, "high_traffic") } else if r.TrafficShare >= 0.01 { score += 10; reasons = append(reasons, "material_traffic") }
 if r.UnknownTrafficShare >= 0.05 { score += 20; reasons = append(reasons, "unknown_traffic") }
 if r.MigrationCompletion < 1.0 { score += 20; reasons = append(reasons, "migration_incomplete") }
 if r.Replacement != "" && !r.ReplacementHealthy { score += 15; reasons = append(reasons, "replacement_unhealthy") }
 if r.Status == model.StatusActive { score += 20; reasons = append(reasons, "not_deprecated") }
 decision := model.DecisionSafe
 if r.ActiveConsumerCount > 0 || r.MigrationCompletion < 1.0 { decision = model.DecisionBlocked } else if score >= 30 { decision = model.DecisionReview }
 return model.DecisionResult{Decision: decision, Score: score, Reasons: reasons, Evidence: map[string]any{
  "endpoint": r.Endpoint, "method": r.Method, "active_consumers": r.ActiveConsumerCount,
  "traffic_share": r.TrafficShare, "unknown_traffic_share": r.UnknownTrafficShare,
  "migration_completion": r.MigrationCompletion, "replacement_healthy": r.ReplacementHealthy,
 }}
}
