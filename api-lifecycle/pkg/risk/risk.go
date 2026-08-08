package risk

import "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"

type Result struct {
 Decision string `json:"decision"`
 Score int `json:"score"`
 Reasons []string `json:"reasons"`
 Evidence map[string]any `json:"evidence"`
}

func Evaluate(e lifecycle.Endpoint) Result {
 score := 0
 reasons := []string{}
 if e.ActiveConsumerCount > 0 { score += 40; reasons = append(reasons, "active_consumers") }
 if e.TrafficShare >= 0.10 { score += 25; reasons = append(reasons, "high_traffic") } else if e.TrafficShare > 0 { score += 10; reasons = append(reasons, "material_traffic") }
 if e.UnknownTrafficShare >= 0.05 { score += 20; reasons = append(reasons, "unknown_traffic") }
 if e.MigrationCompletion < 1 { score += 20; reasons = append(reasons, "migration_incomplete") }
 if e.Replacement != "" && !e.ReplacementHealthy { score += 15; reasons = append(reasons, "replacement_unhealthy") }
 decision := "SAFE"
 if e.ActiveConsumerCount > 0 || e.UnknownTrafficShare >= 0.05 || e.MigrationCompletion < 1 { decision = "BLOCKED" } else if score >= 30 { decision = "REVIEW" }
 return Result{Decision: decision, Score: score, Reasons: reasons, Evidence: map[string]any{
  "endpoint": e.Endpoint, "method": e.Method, "active_consumers": e.ActiveConsumerCount,
  "traffic_share": e.TrafficShare, "unknown_traffic_share": e.UnknownTrafficShare,
  "migration_completion": e.MigrationCompletion, "replacement_healthy": e.ReplacementHealthy,
 }}
}
