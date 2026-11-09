package api

import (
	"encoding/json"
	"net/http"
	"strings"
	"time"

	"github.com/smokblack999-a11y/project-samurai/internal/leads"
)

type LeadHandler struct{}

type createLeadRequest struct {
	ChatID int64  `json:"chat_id"`
	Score  int    `json:"score"`
	Source string `json:"source"`
}

func (LeadHandler) Create(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeLeadError(w, http.StatusMethodNotAllowed, "method not allowed")
		return
	}

	r.Body = http.MaxBytesReader(w, r.Body, 16<<10)
	var in createLeadRequest
	decoder := json.NewDecoder(r.Body)
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&in); err != nil {
		writeLeadError(w, http.StatusBadRequest, "invalid json")
		return
	}
	if in.ChatID == 0 {
		writeLeadError(w, http.StatusBadRequest, "chat_id required")
		return
	}
	if in.Score < 0 || in.Score > 100 {
		writeLeadError(w, http.StatusBadRequest, "score must be 0..100")
		return
	}
	in.Source = strings.TrimSpace(in.Source)
	if in.Source == "" {
		writeLeadError(w, http.StatusBadRequest, "source required")
		return
	}

	out := leads.Lead{
		ChatID:    in.ChatID,
		Score:     in.Score,
		Source:    in.Source,
		Status:    "new",
		CreatedAt: time.Now().UTC(),
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	_ = json.NewEncoder(w).Encode(out)
}

func writeLeadError(w http.ResponseWriter, code int, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(map[string]string{"error": message})
}
