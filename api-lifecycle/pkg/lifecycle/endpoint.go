package lifecycle

// Endpoint is the normalized unit evaluated by the safe-to-sunset engine.
// It is intentionally transport-neutral so logs, OpenAPI and gateways can map into it.
type Endpoint struct {
	Endpoint            string  `json:"endpoint"`
	Method              string  `json:"method"`
	Status              string  `json:"status"`
	ConsumerCount       int     `json:"consumer_count"`
	ActiveConsumers     int     `json:"active_consumer_count"`
	TrafficShare        float64 `json:"traffic_share"`
	UnknownTrafficShare float64 `json:"unknown_traffic_share"`
	MigrationCompletion float64 `json:"migration_completion"`
	ReplacementHealthy  bool    `json:"replacement_healthy"`
}
