package model

import "testing"

func TestValidateRejectsActiveConsumerOverflow(t *testing.T) {
	r := LifecycleRecord{Endpoint: "/v1/x", Method: "GET", Status: StatusDeprecated, ConsumerCount: 2, ActiveConsumerCount: 3, MigrationCompletion: 1}
	if err := r.Validate(); err == nil { t.Fatal("expected validation error") }
}

func TestValidateAcceptsSampleShape(t *testing.T) {
	r := LifecycleRecord{Endpoint: "/v1/orders", Method: "GET", Status: StatusDeprecated, ConsumerCount: 17, ActiveConsumerCount: 5, TrafficShare: .318, UnknownTrafficShare: .174, MigrationCompletion: .42, ReplacementHealthy: true}
	if err := r.Validate(); err != nil { t.Fatalf("unexpected validation error: %v", err) }
}
