package risk

import (
	"testing"
	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
)

func TestBlockedRisk(t *testing.T) {
	e := report.Evidence{
		Score: 10,
		Reasons: []string{"active consumer"},
		AffectedConsumers: []string{"mobile"},
	}

	s := Calculate(e)
	if s.Decision != "BLOCKED" {
		t.Fatalf("expected BLOCKED got %s total=%d", s.Decision, s.Total)
	}
}

func TestSafeRisk(t *testing.T) {
	e := report.Evidence{
		Score: 95,
		Remediations: []string{"migration complete"},
	}

	s := Calculate(e)
	if s.Decision != "SAFE" {
		t.Fatalf("expected SAFE got %s total=%d", s.Decision, s.Total)
	}
}
