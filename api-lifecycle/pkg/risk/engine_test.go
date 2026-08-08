package risk

import (
	"testing"

	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

func TestSafeEndpoint(t *testing.T) {
	e := lifecycle.Endpoint{
		Endpoint: "/v1/orders",
		Method: "GET",
		Status: lifecycle.StatusSunset,
		ConsumerCount: 0,
		ActiveConsumerCount: 0,
		TrafficShare: 0,
		UnknownTrafficShare: 0,
		MigrationCompletion: 1,
		ReplacementHealthy: true,
	}
	got := Evaluate(e)
	if got.Decision != lifecycle.DecisionSafe {
		t.Fatalf("decision = %s, want SAFE; reasons=%v", got.Decision, got.Reasons)
	}
}

func TestActiveConsumerBlocks(t *testing.T) {
	e := lifecycle.Endpoint{
		Status: lifecycle.StatusSunset,
		ActiveConsumerCount: 1,
		MigrationCompletion: 1,
		ReplacementHealthy: true,
	}
	got := Evaluate(e)
	if got.Decision != lifecycle.DecisionBlocked {
		t.Fatalf("decision = %s, want BLOCKED", got.Decision)
	}
}

func TestNonSunsetCannotBeSafe(t *testing.T) {
	e := lifecycle.Endpoint{
		Status: lifecycle.StatusDeprecated,
		MigrationCompletion: 1,
		ReplacementHealthy: true,
	}
	got := Evaluate(e)
	if got.Decision != lifecycle.DecisionBlocked {
		t.Fatalf("decision = %s, want BLOCKED", got.Decision)
	}
}
