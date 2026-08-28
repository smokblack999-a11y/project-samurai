# SAMURAI Telegram Sales

Commercial MVP for Telegram sales/support operations.

## Product

Unified inbox, lead qualification, AI-assisted replies and analytics. TDLib is isolated behind an internal adapter so Telegram transport does not leak into the business domain.

## Run

```bash
go test ./...
go run ./cmd/server
curl http://127.0.0.1:8090/api/system/status
```

## Product rule

Human approval remains the default for AI-generated outbound messages. Do not use the system for spam, bulk unsolicited messaging, or evasion of Telegram limits.
