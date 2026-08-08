package httpmeta

import (
    "net/http"
    "testing"
)

func TestSunset(t *testing.T) {
    h := http.Header{}
    h.Set("Sunset", "Wed, 11 Nov 2026 11:11:11 GMT")
    got, ok := Sunset(h)
    if !ok || got == nil { t.Fatal("expected parsed sunset") }
}

func TestSunsetInvalid(t *testing.T) {
    h := http.Header{}
    h.Set("Sunset", "not-a-date")
    if _, ok := Sunset(h); ok { t.Fatal("invalid date accepted") }
}
