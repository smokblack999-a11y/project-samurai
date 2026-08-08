package risk

import (
	"testing"
	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/model"
)

func TestEvaluateBlocksActiveConsumers(t *testing.T) {
	r := model.LifecycleRecord{Endpoint:"/v1/orders", Method:"GET", Status:model.StatusDeprecated, ActiveConsumerCount:1, MigrationCompletion:1, ReplacementHealthy:true}
	got := Evaluate(r)
	if got.Decision != model.DecisionBlocked { t.Fatalf("expected BLOCKED, got %s", got.Decision) }
}

func TestEvaluateSafeWhenNoConsumersAndMigrated(t *testing.T) {
	r := model.LifecycleRecord{Endpoint:"/v1/orders", Method:"GET", Status:model.StatusSunset, MigrationCompletion:1, ReplacementHealthy:true}
	got := Evaluate(r)
	if got.Decision != model.DecisionSafe { t.Fatalf("expected SAFE, got %s", got.Decision) }
}

func TestEvaluateUnknownTrafficRequiresReview(t *testing.T) {
	r := model.LifecycleRecord{Endpoint:"/v1/orders", Method:"GET", Status:model.StatusDeprecated, UnknownTrafficShare:0.10, MigrationCompletion:1, ReplacementHealthy:true}
	got := Evaluate(r)
	if got.Decision != model.DecisionReview { t.Fatalf("expected REVIEW, got %s", got.Decision) }
}
