package api

import (
    "encoding/json"
    "net/http"
    "github.com/smokblack999-a11y/project-samurai/internal/leads"
)

type LeadHandler struct{}

func (LeadHandler) Create(w http.ResponseWriter, r *http.Request) {
    var in struct { ChatID int64 `json:"chat_id"`; Score int `json:"score"`; Source string `json:"source"` }
    if err := json.NewDecoder(r.Body).Decode(&in); err != nil { http.Error(w, "invalid json", http.StatusBadRequest); return }
    if in.ChatID == 0 { http.Error(w, "chat_id required", http.StatusBadRequest); return }
    if in.Score < 0 || in.Score > 100 { http.Error(w, "score must be 0..100", http.StatusBadRequest); return }
    out := leads.Lead{ChatID: in.ChatID, Score: in.Score, Source: in.Source, Status: "new"}
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(out)
}
