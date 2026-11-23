package api

import (
    "net/http/httptest"
    "strings"
    "testing"
)

func TestCreateLeadRejectsMissingChatID(t *testing.T) {
    req := httptest.NewRequest("POST", "/api/leads", strings.NewReader(`{"score":50}`))
    rec := httptest.NewRecorder()
    (LeadHandler{}).Create(rec, req)
    if rec.Code != 400 { t.Fatalf("expected 400, got %d", rec.Code) }
}

func TestCreateLeadAcceptsValidLead(t *testing.T) {
    req := httptest.NewRequest("POST", "/api/leads", strings.NewReader(`{"chat_id":123,"score":80,"source":"telegram"}`))
    rec := httptest.NewRecorder()
    (LeadHandler{}).Create(rec, req)
    if rec.Code != 201 { t.Fatalf("expected 201, got %d", rec.Code) }
}
