package lifecycle

import "time"

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
