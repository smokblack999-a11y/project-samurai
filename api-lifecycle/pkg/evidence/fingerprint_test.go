package evidence

import "testing"

func TestFingerprintStable(t *testing.T) { a, _ := Fingerprint(map[string]any{"decision":"REVIEW","score":80}); b, _ := Fingerprint(map[string]any{"decision":"REVIEW","score":80}); if a != b { t.Fatalf("fingerprint changed: %s != %s", a, b) } }
