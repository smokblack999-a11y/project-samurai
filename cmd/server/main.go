package main

import (
    "encoding/json"
    "log"
    "net/http"
    "os"
    "time"
)

type Status struct {
    OK      bool   `json:"ok"`
    Service string `json:"service"`
    Version string `json:"version"`
    Uptime  string `json:"uptime"`
    Telegram struct {
        Enabled   bool   `json:"enabled"`
        Connected bool   `json:"connected"`
        Driver    string `json:"driver"`
    } `json:"telegram"`
    Database struct { OK bool `json:"ok"` } `json:"database"`
    AI struct { Enabled bool `json:"enabled"` } `json:"ai"`
}

var started = time.Now()

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/api/system/status", statusHandler)
    mux.HandleFunc("/health", func(w http.ResponseWriter, _ *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]any{"ok": true})
    })

    addr := os.Getenv("SAMURAI_ADDR")
    if addr == "" { addr = ":8090" }
    log.Printf("samurai-telegram-sales listening on %s", addr)
    log.Fatal(http.ListenAndServe(addr, mux))
}

func statusHandler(w http.ResponseWriter, _ *http.Request) {
    var s Status
    s.OK, s.Service, s.Version, s.Uptime = true, "samurai-telegram-sales", "0.1.0", time.Since(started).Round(time.Second).String()
    s.Telegram.Enabled = os.Getenv("TDLIB_ENABLED") == "1"
    s.Telegram.Connected = false
    s.Telegram.Driver = "tdjson"
    s.Database.OK = true
    s.AI.Enabled = os.Getenv("AI_ENABLED") == "1"
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(s)
}
