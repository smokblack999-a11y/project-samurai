package main

import (
	"encoding/json"
	"log"
	"net/http"
	"time"

	"github.com/smokblack999-a11y/project-samurai/internal/api"
	"github.com/smokblack999-a11y/project-samurai/internal/config"
	httpx "github.com/smokblack999-a11y/project-samurai/internal/httpx"
	"github.com/smokblack999-a11y/project-samurai/internal/system"
)

var started = time.Now()

func main() {
	cfg := config.Load()
	mux := http.NewServeMux()
	mux.HandleFunc("/api/system/status", statusHandler(cfg))
	mux.HandleFunc("/api/leads", (api.LeadHandler{}).Create)
	mux.HandleFunc("/health", healthHandler)

	addr := cfg.Addr
	server := &http.Server{
		Addr:              addr,
		Handler:           httpx.Security(mux),
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       15 * time.Second,
		WriteTimeout:      15 * time.Second,
		IdleTimeout:       60 * time.Second,
	}

	log.Printf("samurai-telegram-sales listening on %s", addr)
	log.Fatal(server.ListenAndServe())
}

func statusHandler(cfg config.Config) http.HandlerFunc {
	return func(w http.ResponseWriter, _ *http.Request) {
		writeJSON(w, http.StatusOK, system.BuildStatus(
			cfg.Version,
			started,
			cfg.TDLibEnabled,
			cfg.AIEnabled,
		))
	}
}

func healthHandler(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]any{"ok": true})
}

func writeJSON(w http.ResponseWriter, code int, value any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(value)
}
