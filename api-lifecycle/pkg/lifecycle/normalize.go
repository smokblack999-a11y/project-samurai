package lifecycle

import "strings"

// Normalize makes inputs deterministic before validation and scoring.
func (e Endpoint) Normalize() Endpoint {
	e.Endpoint = strings.TrimSpace(e.Endpoint)
	e.Method = strings.ToUpper(strings.TrimSpace(e.Method))
	if e.MigrationCompletion < 0 { e.MigrationCompletion = 0 }
	if e.MigrationCompletion > 1 { e.MigrationCompletion = 1 }
	if e.TrafficShare < 0 { e.TrafficShare = 0 }
	if e.TrafficShare > 1 { e.TrafficShare = 1 }
	if e.UnknownTrafficShare < 0 { e.UnknownTrafficShare = 0 }
	if e.UnknownTrafficShare > 1 { e.UnknownTrafficShare = 1 }
	return e
}
