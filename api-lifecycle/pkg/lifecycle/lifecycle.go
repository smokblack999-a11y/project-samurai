package lifecycle

import "fmt"

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
 ConsumerCount int `json:"consumer_count"`
 ActiveConsumerCount int `json:"active_consumer_count"`
 TrafficShare float64 `json:"traffic_share"`
 UnknownTrafficShare float64 `json:"unknown_traffic_share"`
 MigrationCompletion float64 `json:"migration_completion"`
 Replacement string `json:"replacement,omitempty"`
 ReplacementHealthy bool `json:"replacement_healthy"`
}

func (e Endpoint) Validate() error {
 if e.Endpoint == "" { return fmt.Errorf("endpoint is required") }
 if e.Method == "" { return fmt.Errorf("method is required") }
 if e.ConsumerCount < 0 || e.ActiveConsumerCount < 0 { return fmt.Errorf("consumer counts cannot be negative") }
 if e.TrafficShare < 0 || e.TrafficShare > 1 || e.UnknownTrafficShare < 0 || e.UnknownTrafficShare > 1 || e.MigrationCompletion < 0 || e.MigrationCompletion > 1 { return fmt.Errorf("ratio must be between 0 and 1") }
 if e.ActiveConsumerCount > e.ConsumerCount { return fmt.Errorf("active consumers exceed total consumers") }
 return nil
}
