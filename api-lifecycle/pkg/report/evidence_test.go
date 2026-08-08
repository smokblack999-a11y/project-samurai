package report

import "testing"

func TestFingerprintStable(t *testing.T) {
    e := Evidence{Endpoint:"/v1/orders", Method:"GET", Decision:"REVIEW", Reasons:[]string{"active consumers remain observed"}}
    a, err := Fingerprint(e)
    if err != nil { t.Fatal(err) }
    b, err := Fingerprint(e)
    if err != nil { t.Fatal(err) }
    if a == "" || a != b { t.Fatalf("unstable fingerprint: %q %q", a, b) }
}
