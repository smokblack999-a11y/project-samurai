package model

import "fmt"

func (r LifecycleRecord) Validate() error {
	if r.Endpoint == "" { return fmt.Errorf("endpoint is required") }
	if r.Method == "" { return fmt.Errorf("method is required") }
	if r.Status != StatusActive && r.Status != StatusDeprecated && r.Status != StatusSunset { return fmt.Errorf("invalid status: %q", r.Status) }
	if r.ConsumerCount < 0 || r.ActiveConsumerCount < 0 { return fmt.Errorf("consumer counts cannot be negative") }
	if r.ActiveConsumerCount > r.ConsumerCount { return fmt.Errorf("active consumers exceed total consumers") }
	if r.TrafficShare < 0 || r.TrafficShare > 1 { return fmt.Errorf("traffic_share must be between 0 and 1") }
	if r.UnknownTrafficShare < 0 || r.UnknownTrafficShare > 1 { return fmt.Errorf("unknown_traffic_share must be between 0 and 1") }
	if r.MigrationCompletion < 0 || r.MigrationCompletion > 1 { return fmt.Errorf("migration_completion must be between 0 and 1") }
	return nil
}
