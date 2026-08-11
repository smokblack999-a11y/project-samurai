package risk

import (
    "testing"
    "time"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
)

func TestBlockedRisk(t *testing.T) {
    e := report.Evidence{
        Endpoint: "/v1/orders",
        Method: "GET",
        ConsumerCount: 3,
        ActiveConsumerCount: 2,
        UnknownTrafficShare: 0.25,
        MigrationCompletion: 0.2,
        Replacement: "",
        ReplacementHealthy: false,
    }
    s := Calculate(e)
    if s.Decision != "BLOCKED" {
        t.Fatalf("expected BLOCKED got %s total=%d", s.Decision, s.Total)
    }
}

func TestSafeRisk(t *testing.T) {
    sunset := time.Now().UTC().Add(24 * time.Hour)
    e := report.Evidence{
        Endpoint: "/v1/orders",
        Method: "GET",
        ConsumerCount: 10,
        ActiveConsumerCount: 0,
        UnknownTrafficShare: 0,
        MigrationCompletion: 1,
        Replacement: "/v2/orders",
        ReplacementHealthy: true,
        Sunset: &sunset,
    }
    s := Calculate(e)
    if s.Decision != "SAFE" {
        t.Fatalf("expected SAFE got %s total=%d", s.Decision, s.Total)
    }
    if s.Total != 110 {
        t.Fatalf("expected current weighted total 110, got %d", s.Total)
    }
}
