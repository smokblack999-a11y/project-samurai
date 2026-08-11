package lifecycle

import (
	"fmt"
	"strings"
	"time"
)

type Status string

const (
	StatusActive Status = "active"
	StatusDeprecated Status = "deprecated"
	StatusSunset Status = "sunset"
)

type Endpoint struct {
	Endpoint string `json:"endpoint"`
	Method string `json:"method"`
	Status Status `json:"status"`
	Deprecation *time.Time `json:"deprecation,omitempty"`
	Sunset *time.Time `json:"sunset,omitempty"`
	Replacement string `json:"replacement,omitempty"`
	ConsumerCount int `json:"consumer_count"`
	ActiveConsumerCount int `json:"active_consumer_count"`
	TrafficShare float64 `json:"traffic_share"`
	UnknownTrafficShare float64 `json:"unknown_traffic_share"`
	MigrationCompletion float64 `json:"migration_completion"`
	ReplacementHealthy bool `json:"replacement_healthy"`
}

func (e Endpoint) Validate() error {
	if strings.TrimSpace(e.Endpoint) == "" { return fmt.Errorf("endpoint is required") }
	switch strings.ToUpper(strings.TrimSpace(e.Method)) {
	case "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS":
	default: return fmt.Errorf("unsupported method: %q", e.Method)
	}
	switch e.Status {
	case StatusActive, StatusDeprecated, StatusSunset:
	default: return fmt.Errorf("invalid status: %q", e.Status)
	}
	if e.ConsumerCount < 0 || e.ActiveConsumerCount < 0 { return fmt.Errorf("consumer counts cannot be negative") }
	if e.ActiveConsumerCount > e.ConsumerCount { return fmt.Errorf("active consumers exceed total consumers") }
	if e.TrafficShare < 0 || e.TrafficShare > 1 { return fmt.Errorf("traffic_share must be between 0 and 1") }
	if e.UnknownTrafficShare < 0 || e.UnknownTrafficShare > 1 { return fmt.Errorf("unknown_traffic_share must be between 0 and 1") }
	if e.MigrationCompletion < 0 || e.MigrationCompletion > 1 { return fmt.Errorf("migration_completion must be between 0 and 1") }
	if e.Status == StatusSunset && e.Sunset == nil { return fmt.Errorf("sunset timestamp is required for sunset status") }
	return nil
}

type ConsumerObservation struct {
	ConsumerID string `json:"consumer_id"`
	Endpoint string `json:"endpoint"`
	Requests int64 `json:"requests"`
	LastSeen time.Time `json:"last_seen"`
	Migrated bool `json:"migrated"`
	Known bool `json:"known"`
}

type Decision string

const (
	DecisionSafe Decision = "SAFE"
	DecisionReview Decision = "REVIEW"
	DecisionBlocked Decision = "BLOCKED"
)

type RiskResult struct {
	Decision Decision `json:"decision"`
	Score int `json:"score"`
	Confidence int `json:"confidence"`
	Reasons []string `json:"reasons"`
	Remediations []string `json:"remediations"`
}
