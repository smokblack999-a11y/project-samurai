package system

import "time"

type Status struct {
	OK      bool   `json:"ok"`
	Service string `json:"service"`
	Version string `json:"version"`
	Uptime  string `json:"uptime"`
	Telegram Component `json:"telegram"`
	Database Component `json:"database"`
	AI       Component `json:"ai"`
}

type Component struct {
	Enabled bool   `json:"enabled"`
	Ready   bool   `json:"ready"`
	Driver  string `json:"driver,omitempty"`
	Reason  string `json:"reason,omitempty"`
}

func BuildStatus(version string, started time.Time, tdEnabled, aiEnabled bool) Status {
	return Status{
		OK: true, Service: "samurai-telegram-sales", Version: version,
		Uptime: time.Since(started).Round(time.Second).String(),
		Telegram: Component{Enabled: tdEnabled, Ready: false, Driver: "tdjson", Reason: "adapter not connected"},
		Database: Component{Enabled: true, Ready: true, Driver: "sqlite"},
		AI: Component{Enabled: aiEnabled, Ready: false, Driver: "provider", Reason: "provider health check not configured"},
	}
}
