package risk

import (
	"testing"

	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/model"
)

func TestEvaluateBlocksActiveConsumers(t *testing.T) {
	r := model.LifecycleRecord{Endpoint: "/v1/orders", Method: "GET", Status: model.StatusDeprecated, ActiveConsumerCount: 5, MigrationCompletion: 0.42, TrafficShare: 0.318, UnknownTrafficShare: 0.174, Replacement: "/v2/orders", ReplacementHealthy: true}
	got := New().Evaluate(r)
	if got.Decision != model.DecisionBlocked { t.Fatalf("decision = %s, want BLOCKED", got.Decision) }
	if got.Score != 95 { t.Fatalf("score = %d, want 95", got.Score) }
}

func TestEvaluateSafeWhenFullyMigrated(t *testing.T) {
	r := model.LifecycleRecord{Endpoint: "/v1/old", Method: "GET", Status: model.StatusDeprecated, MigrationCompletion: 1, Replacement: "/v2/old", ReplacementHealthy: true}
	got := New().Evaluate(r)
	if got.Decision != model.DecisionSafe { t.Fatalf("decision = %s, want SAFE", got.Decision) }
	if got.Score != 0 { t.Fatalf("score = %d, want 0", got.Score) }
}
