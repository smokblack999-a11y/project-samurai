package risk

import (
	"testing"

	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

func TestEvaluateBlocksActiveConsumers(t *testing.T) {
	r := Evaluate(lifecycle.Endpoint{
		ConsumerCount: 5,
		ActiveConsumers: 5,
		TrafficShare: 0.318,
		UnknownTrafficShare: 0.174,
		MigrationCompletion: 0.42,
		ReplacementHealthy: true,
	})
	if r.Decision != Blocked {
		t.Fatalf("expected BLOCKED, got %s (score=%d)", r.Decision, r.Score)
	}
}

func TestEvaluateSafeWhenUnused(t *testing.T) {
	r := Evaluate(lifecycle.Endpoint{ReplacementHealthy: true})
	if r.Decision != Safe || r.Score != 0 {
		t.Fatalf("expected SAFE/0, got %s/%d", r.Decision, r.Score)
	}
}

func TestEvaluateReviewBoundary(t *testing.T) {
	r := Evaluate(lifecycle.Endpoint{
		ActiveConsumers: 1,
		ReplacementHealthy: true,
	})
	if r.Decision != Review {
		t.Fatalf("expected REVIEW, got %s (score=%d)", r.Decision, r.Score)
	}
}
