package ai

import "testing"

func TestEvaluateDefaultsToDraft(t *testing.T) {
	if got := Evaluate(0.99, false, false); got != DraftOnly {
		t.Fatalf("expected %q, got %q", DraftOnly, got)
	}
}

func TestEvaluateBlocksSensitive(t *testing.T) {
	if got := Evaluate(0.99, true, true); got != HumanRequired {
		t.Fatalf("expected %q, got %q", HumanRequired, got)
	}
}

func TestEvaluateAllowsExplicitHighConfidenceApproval(t *testing.T) {
	if got := Evaluate(0.95, false, true); got != AllowSend {
		t.Fatalf("expected %q, got %q", AllowSend, got)
	}
}
