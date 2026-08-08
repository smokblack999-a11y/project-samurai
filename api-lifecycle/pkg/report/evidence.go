package report

import (
    "encoding/json"
    "time"
)

type Evidence struct {
    GeneratedAt time.Time `json:"generated_at"`
    Endpoint string `json:"endpoint"`
    Method string `json:"method"`
    Status string `json:"status"`
    Sunset *time.Time `json:"sunset,omitempty"`
    Replacement string `json:"replacement,omitempty"`
    ConsumerCount int `json:"consumer_count"`
    ActiveConsumerCount int `json:"active_consumer_count"`
    UnknownTrafficShare float64 `json:"unknown_traffic_share"`
    MigrationCompletion float64 `json:"migration_completion"`
    ReplacementHealthy bool `json:"replacement_healthy"`
    Decision string `json:"decision"`
    Reasons []string `json:"reasons"`
}

func Marshal(e Evidence) ([]byte, error) { return json.MarshalIndent(e, "", "  ") }
