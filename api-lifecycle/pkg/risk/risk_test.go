package risk

import (
	"testing"
	"time"
)

func TestEvaluateBlocksActiveConsumers(t *testing.T) {
	r := Evaluate(Input{
		ConsumerCount: 5,
		ActiveConsumers: 5,
		TrafficShare: 0.318,
		UnknownTrafficShare: 0.174,
		MigrationCompletion: 0.42,
		ReplacementHealthy: true,
	}, time.Now())
	if r.Decision != Blocked {
		t.Fatalf("expected BLOCKED, got %s (score=%d)", r.Decision, r.Score)
	}
}

func TestEvaluateSafeWhenUnused(t *testing.T) {
	r := Evaluate(Input{ReplacementHealthy: true}, time.Now())
	if r.Decision != Safe || r.Score != 0 {
		t.Fatalf("expected SAFE/0, got %s/%d", r.Decision, r.Score)
	}
}

func TestPastSunsetIsOnlyAReasonWhenOtherwiseSafe(t *testing.T) {
	past := time.Now().Add(-time.Hour)
	r := Evaluate(Input{ReplacementHealthy: true, Sunset: &past}, time.Now())
	if r.Decision != Safe {
		t.Fatalf("expected SAFE, got %s", r.Decision)
	}
	if len(r.Reasons) != 1 || r.Reasons[0] != "sunset time has passed" {
		t.Fatalf("unexpected reasons: %#v", r.Reasons)
	}
}
