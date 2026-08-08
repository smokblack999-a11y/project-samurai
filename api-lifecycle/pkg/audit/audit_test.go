package audit

import (
    "testing"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/consumer"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/risk"
)

func TestRunBlocksUnknownTraffic(t *testing.T) {
    got := Run(Input{
        Endpoint: lifecycle.Endpoint{Endpoint: "/v1/orders", Method: "GET"},
        Records: []consumer.AccessRecord{{Method: "GET", Path: "/v1/orders", Consumer: ""}},
        Replacement: "/v2/orders",
        ReplacementHealthy: true,
        MigrationCompletion: 1,
        Policy: risk.DefaultPolicy,
    })
    if got.Decision != "BLOCKED" { t.Fatalf("decision=%s", got.Decision) }
}

func TestRunReviewsActiveConsumers(t *testing.T) {
    got := Run(Input{
        Endpoint: lifecycle.Endpoint{Endpoint: "/v1/orders", Method: "GET"},
        Records: []consumer.AccessRecord{{Method: "GET", Path: "/v1/orders", Consumer: "billing"}},
        Replacement: "/v2/orders",
        ReplacementHealthy: true,
        MigrationCompletion: 1,
        Policy: risk.DefaultPolicy,
    })
    if got.Decision != "REVIEW" { t.Fatalf("decision=%s", got.Decision) }
}
