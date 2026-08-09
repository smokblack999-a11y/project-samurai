package main

import (
	"encoding/json"
	"log"
	"net/http"
	"time"

	"github.com/smokblack999-a11y/project-samurai/internal/config"
	"github.com/smokblack999-a11y/project-samurai/internal/system"
)

var started = time.Now()

func main() {
	cfg := config.Load()
	mux := http.NewServeMux()
	mux.HandleFunc("/api/system/status", statusHandler(cfg))
	mux.HandleFunc("/health", healthHandler)

	addr := cfg.Addr
	log.Printf("samurai-telegram-sales listening on %s", addr)
	log.Fatal(http.ListenAndServe(addr, mux))
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
