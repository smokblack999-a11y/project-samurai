package config

import "os"

type Config struct {
	Addr        string
	Version     string
	TDLibEnabled bool
	AIEnabled   bool
}

func Load() Config {
	return Config{
		Addr:         env("SAMURAI_ADDR", ":8090"),
		Version:      env("SAMURAI_VERSION", "0.2.0"),
		TDLibEnabled: os.Getenv("TDLIB_ENABLED") == "1",
		AIEnabled:    os.Getenv("AI_ENABLED") == "1",
	}
}

func env(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}
