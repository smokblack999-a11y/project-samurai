package risk

// Thresholds are intentionally explicit and versionable. Changing them changes
// production decisions, so they belong in code review rather than hidden config.
type Thresholds struct {
	HighTrafficShare    float64
	HighUnknownShare    float64
	CompleteMigration   float64
}

var DefaultThresholds = Thresholds{
	HighTrafficShare:  0.20,
	HighUnknownShare:  0.10,
	CompleteMigration: 1.00,
}
