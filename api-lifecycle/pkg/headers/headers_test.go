package headers

import (
    "net/http"
    "testing"
    "time"
)

func TestApplyAndParse(t *testing.T) {
    h := make(http.Header)
    dep := time.Unix(1754006400, 0).UTC()
    sunset := time.Date(2026, 12, 1, 0, 0, 0, 0, time.UTC)
    Apply(h, &dep, &sunset, "/v2/orders")
    gotDep, err := ParseDeprecation(h.Get(Deprecation)); if err != nil { t.Fatal(err) }
    if !gotDep.Equal(dep) { t.Fatalf("deprecation=%s want=%s", gotDep, dep) }
    gotSunset, err := ParseSunset(h.Get(Sunset)); if err != nil { t.Fatal(err) }
    if !gotSunset.Equal(sunset) { t.Fatalf("sunset=%s want=%s", gotSunset, sunset) }
    if h.Get(Link) == "" { t.Fatal("missing successor-version Link") }
}
