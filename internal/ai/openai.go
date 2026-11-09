package ai

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/smokblack999-a11y/project-samurai/internal/leads"
)

type OpenAIProvider struct {
	APIKey string
	Model  string
	Client *http.Client
}

func NewOpenAIProvider() *OpenAIProvider {
	model := os.Getenv("OPENAI_MODEL")
	if model == "" {
		model = "gpt-5-mini"
	}
	return &OpenAIProvider{
		APIKey: os.Getenv("OPENAI_API_KEY"),
		Model:  model,
		Client: &http.Client{Timeout: 30 * time.Second},
	}
}

func (p *OpenAIProvider) Suggest(ctx context.Context, lead leads.Lead, customerMessage string) (Suggestion, error) {
	if p.APIKey == "" {
		return Suggestion{}, fmt.Errorf("OPENAI_API_KEY is not configured")
	}

	prompt := fmt.Sprintf(
		"You are a sales/support copilot. Lead score: %d. Source: %s. Customer message: %s. Return a concise draft reply. Never claim actions that were not taken. The operator must approve the reply before sending.",
		lead.Score, lead.Source, customerMessage,
	)

	payload := map[string]any{
		"model": p.Model,
		"input": prompt,
		"store": false,
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return Suggestion{}, err
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, "https://api.openai.com/v1/responses", bytes.NewReader(body))
	if err != nil {
		return Suggestion{}, err
	}
	req.Header.Set("Authorization", "Bearer "+p.APIKey)
	req.Header.Set("Content-Type", "application/json")

	resp, err := p.Client.Do(req)
	if err != nil {
		return Suggestion{}, err
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return Suggestion{}, fmt.Errorf("openai responses API returned %s", resp.Status)
	}

	var result struct {
		OutputText string `json:"output_text"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return Suggestion{}, err
	}
	if result.OutputText == "" {
		return Suggestion{}, fmt.Errorf("openai response contained no output_text")
	}

	return Suggestion{
		Intent:        "sales_support",
		Summary:       "AI-generated draft based on the latest customer message",
		Reply:         result.OutputText,
		Confidence:    0.0,
		RequiresHuman: true,
	}, nil
}
