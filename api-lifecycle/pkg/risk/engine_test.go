package risk

import (
	"testing"
	"time"

	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

func TestSafeEndpoint(t *testing.T) {
	sunset := time.Date(2026, 12, 1, 0, 0, 0, 0, time.UTC)
	e := lifecycle.Endpoint{Endpoint:"/v1/orders", Method:"GET", Status:lifecycle.StatusSunset, Sunset:&sunset, ConsumerCount:0, ActiveConsumerCount:0, TrafficShare:0, UnknownTrafficShare:0, MigrationCompletion:1, ReplacementHealthy:true}
	got := Evaluate(e)
	if got.Decision != lifecycle.DecisionSafe { t.Fatalf("decision = %s, want SAFE; reasons=%v", got.Decision, got.Reasons) }
}

func TestActiveConsumerBlocks(t *testing.T) {
	sunset := time.Now().UTC().Add(24 * time.Hour)
	e := lifecycle.Endpoint{Status:lifecycle.StatusSunset, Sunset:&sunset, ActiveConsumerCount:1, MigrationCompletion:1}
	got := Evaluate(e)
	if got.Decision != lifecycle.DecisionBlocked { t.Fatalf("decision = %s, want BLOCKED", got.Decision) }
}

func TestNonSunsetCannotBeSafe(t *testing.T) {
	e := lifecycle.Endpoint{Status:lifecycle.StatusDeprecated, MigrationCompletion:1}
	got := Evaluate(e)
	if got.Decision != lifecycle.DecisionBlocked { t.Fatalf("decision = %s, want BLOCKED", got.Decision) }
}

func TestSunsetRequiresTimestamp(t *testing.T) {
	e := lifecycle.Endpoint{Status:lifecycle.StatusSunset}
	got := Evaluate(e)
	if got.Decision != lifecycle.DecisionBlocked { t.Fatalf("decision = %s, want BLOCKED", got.Decision) }
}
