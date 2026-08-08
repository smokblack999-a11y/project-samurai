package risk

import (
	"testing"
	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/model"
)

func TestHighRiskDeprecatedAPIIsBlocked(t *testing.T) {
	r := model.LifecycleRecord{Endpoint:"/v1/orders", Method:"GET", Status:model.StatusDeprecated, ActiveConsumerCount:5, TrafficShare:.318, UnknownTrafficShare:.174, MigrationCompletion:.42, Replacement:"/v2/orders", ReplacementHealthy:true}
	got := New().Evaluate(r)
	if got.Decision != model.RiskBlocked { t.Fatalf("expected BLOCKED, got %s", got.Decision) }
}

func TestActiveAPIIsSafe(t *testing.T) {
	r := model.LifecycleRecord{Endpoint:"/v3/orders", Method:"GET", Status:model.StatusActive, ActiveConsumerCount:10, TrafficShare:.8}
	got := New().Evaluate(r)
	if got.Decision != model.RiskSafe { t.Fatalf("expected SAFE, got %s", got.Decision) }
}

func TestUnknownTrafficRequiresReview(t *testing.T) {
	r := model.LifecycleRecord{Endpoint:"/v1/orders", Method:"GET", Status:model.StatusDeprecated, UnknownTrafficShare:.10, MigrationCompletion:1, ReplacementHealthy:true}
	got := New().Evaluate(r)
	if got.Decision != model.RiskReview { t.Fatalf("expected REVIEW, got %s", got.Decision) }
}
