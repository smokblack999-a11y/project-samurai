package risk

import (
 "testing"
 "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

func TestUnsafeEndpointIsBlocked(t *testing.T) {
 r := Evaluate(lifecycle.Endpoint{Endpoint:"/v1/payments", Method:"POST", Status:lifecycle.StatusDeprecated, ActiveConsumerCount:5, TrafficShare:.318, UnknownTrafficShare:.174, MigrationCompletion:.42, Replacement:"/v2/payments", ReplacementHealthy:true})
 if r.Decision != "BLOCKED" { t.Fatalf("decision=%s, want BLOCKED", r.Decision) }
}

func TestUnusedMigratedEndpointIsSafe(t *testing.T) {
 r := Evaluate(lifecycle.Endpoint{Endpoint:"/v1/archive", Method:"GET", Status:lifecycle.StatusDeprecated, MigrationCompletion:1, Replacement:"/v2/archive", ReplacementHealthy:true})
 if r.Decision != "SAFE" { t.Fatalf("decision=%s, want SAFE", r.Decision) }
}

func TestUnknownTrafficBlocks(t *testing.T) {
 r := Evaluate(lifecycle.Endpoint{Endpoint:"/v1/users", Method:"GET", Status:lifecycle.StatusDeprecated, UnknownTrafficShare:.10, MigrationCompletion:1})
 if r.Decision != "BLOCKED" { t.Fatalf("decision=%s, want BLOCKED", r.Decision) }
}
