package httpmeta

import (
    "net/http"
    "time"
)

// Sunset returns the RFC 8594 Sunset timestamp as a hint. It deliberately
// does not convert the hint into a shutdown decision by itself.
func Sunset(h http.Header) (*time.Time, bool) {
    raw := h.Get("Sunset")
    if raw == "" { return nil, false }
    t, err := http.ParseTime(raw)
    if err != nil { return nil, false }
    return &t, true
}
