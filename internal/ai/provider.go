package ai

import (
	"context"

	"github.com/smokblack999-a11y/project-samurai/internal/leads"
)

type Suggestion struct {
	Intent          string  `json:"intent"`
	Summary         string  `json:"summary"`
	Reply           string  `json:"reply"`
	Confidence      float64 `json:"confidence"`
	RequiresHuman   bool    `json:"requires_human"`
}

type Provider interface {
	Suggest(ctx context.Context, lead leads.Lead, customerMessage string) (Suggestion, error)
}
