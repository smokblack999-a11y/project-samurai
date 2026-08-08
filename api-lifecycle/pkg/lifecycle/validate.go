package lifecycle

import "fmt"

func (e Endpoint) Validate() error {
    if e.Endpoint == "" { return fmt.Errorf("endpoint is required") }
    if e.Method == "" { return fmt.Errorf("method is required") }
    switch e.Status {
    case StatusActive, StatusDeprecated, StatusSunset:
    default: return fmt.Errorf("invalid status: %q", e.Status)
    }
    if e.ConsumerCount < 0 || e.ActiveConsumerCount < 0 { return fmt.Errorf("consumer counts cannot be negative") }
    if e.ActiveConsumerCount > e.ConsumerCount { return fmt.Errorf("active consumers exceed total consumers") }
    if e.TrafficShare < 0 || e.TrafficShare > 1 { return fmt.Errorf("traffic_share must be between 0 and 1") }
    if e.UnknownTrafficShare < 0 || e.UnknownTrafficShare > 1 { return fmt.Errorf("unknown_traffic_share must be between 0 and 1") }
    if e.MigrationCompletion < 0 || e.MigrationCompletion > 1 { return fmt.Errorf("migration_completion must be between 0 and 1") }
    if e.Status == StatusSunset && e.Sunset.IsZero() { return fmt.Errorf("sunset timestamp is required for sunset status") }
    return nil
}
