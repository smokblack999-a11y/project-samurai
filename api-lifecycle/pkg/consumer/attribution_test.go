package consumer

import (
    "testing"
    "time"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

func TestAttributePreservesUnknownTraffic(t *testing.T) {
    endpoint := lifecycle.Endpoint{Endpoint: "/v1/users/{id}", Method: "GET"}
    records := []AccessRecord{
        {Timestamp: time.Now(), Method: "GET", Path: "/v1/users/42", Consumer: "billing"},
        {Timestamp: time.Now(), Method: "GET", Path: "/v1/users/43", Consumer: ""},
        {Timestamp: time.Now(), Method: "POST", Path: "/v1/users/44", Consumer: "ignored"},
    }
    got := Attribute(endpoint, records)
    if got.Requests != 2 || got.KnownRequests != 1 || got.UnknownRequests != 1 {
        t.Fatalf("unexpected attribution: %+v", got)
    }
    if got.ConsumerCount != 1 || got.ActiveConsumerCount != 1 {
        t.Fatalf("unexpected consumers: %+v", got)
    }
    if got.UnknownTrafficShare != 0.5 { t.Fatalf("unexpected unknown share: %v", got.UnknownTrafficShare) }
}
