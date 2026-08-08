package risk

import "time"

type Input struct {
	ConsumerCount       int
	ActiveConsumers     int
	TrafficShare        float64
	UnknownTrafficShare float64
	MigrationCompletion float64
	ReplacementHealthy  bool
	Sunset              *time.Time
}

type Decision string

const (
	Safe    Decision = "SAFE"
	Review  Decision = "REVIEW"
	Blocked Decision = "BLOCKED"
)

type Result struct {
	Score       int      `json:"score"`
	Decision    Decision `json:"decision"`
	Confidence  int      `json:"confidence"`
	Reasons     []string `json:"reasons"`
}

// Evaluate is deliberately deterministic. It does not pretend that an LLM
// can prove an API is safe to remove. The score is explainable and bounded.
func Evaluate(in Input, now time.Time) Result {
	score := 0
	reasons := make([]string, 0, 8)

	if in.ActiveConsumers > 0 {
		score += min(35, in.ActiveConsumers*7)
		reasons = append(reasons, "active consumers remain")
	}
	if in.TrafficShare > 0.01 {
		score += min(25, int(in.TrafficShare*100))
		reasons = append(reasons, "meaningful traffic remains")
	}
	if in.UnknownTrafficShare > 0.01 {
		score += min(20, int(in.UnknownTrafficShare*100))
		reasons = append(reasons, "unknown traffic remains")
	}
	if in.MigrationCompletion < 1 {
		score += min(15, int((1-in.MigrationCompletion)*15))
		reasons = append(reasons, "migration is incomplete")
	}
	if !in.ReplacementHealthy {
		score += 15
		reasons = append(reasons, "replacement is not healthy")
	}
	if in.ConsumerCount == 0 && in.TrafficShare == 0 && in.UnknownTrafficShare == 0 {
		score = 0
	}

	if score > 100 {
		score = 100
	}

	decision := Safe
	switch {
	case score >= 50:
		decision = Blocked
	case score >= 20:
		decision = Review
	}

	confidence := 100 - score
	if in.ConsumerCount == 0 {
		confidence = 100
	}
	if in.Sunset != nil && in.Sunset.Before(now) && decision == Safe {
		reasons = append(reasons, "sunset time has passed")
	}

	return Result{Score: score, Decision: decision, Confidence: confidence, Reasons: reasons}
}

func min(a, b int) int {
	if a < b { return a }
	return b
}
