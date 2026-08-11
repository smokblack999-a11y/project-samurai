package risk

import "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"

type Score struct {
	ConsumerCoverage   int `json:"consumer_coverage"`
	ReplacementReady   int `json:"replacement_ready"`
	TrafficHealth      int `json:"traffic_health"`
	UnknownConsumers   int `json:"unknown_consumers"`
	MigrationEvidence  int `json:"migration_evidence"`
	SunsetPolicy       int `json:"sunset_policy"`
	Total              int `json:"total"`
	Decision           string `json:"decision"`
}

func Calculate(e report.Evidence) Score {
	s := Score{}

	if len(e.AffectedConsumers) > 0 {
		s.ConsumerCoverage = 30
	}
	if len(e.Reasons) == 0 {
		s.ReplacementReady = 25
	}
	if e.Score >= 70 {
		s.TrafficHealth = 20
	}
	if len(e.AffectedConsumers) == 0 {
		s.UnknownConsumers = 15
	}
	if len(e.Remediations) > 0 {
		s.MigrationEvidence = 10
	}

	// RFC 8594 sunset information is treated as a signal, not a guarantee.
	s.SunsetPolicy = 10

	s.Total = s.ConsumerCoverage + s.ReplacementReady + s.TrafficHealth + s.UnknownConsumers + s.MigrationEvidence + s.SunsetPolicy

	switch {
	case s.Total >= 85:
		s.Decision = "SAFE"
	case s.Total >= 50:
		s.Decision = "REVIEW"
	default:
		s.Decision = "BLOCKED"
	}

	return s
}
