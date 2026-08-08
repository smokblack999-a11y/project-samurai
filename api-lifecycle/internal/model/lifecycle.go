package model

import "time"

type Status string

const (
	StatusActive Status = "active"
	StatusDeprecated Status = "deprecated"
	StatusSunset Status = "sunset"
)

type LifecycleRecord struct {
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

type RiskLevel string
const (
	RiskSafe RiskLevel = "SAFE"
	RiskReview RiskLevel = "REVIEW"
	RiskBlocked RiskLevel = "BLOCKED"
)

type RiskDecision struct {
	Decision RiskLevel `json:"decision"`
	Score int `json:"score"`
	Reasons []string `json:"reasons"`
}
