package report

import "testing"

func TestBuildBundlePriority(t *testing.T) {
    cases := []struct{ decision, want string }{
        {"SAFE", "low"},
        {"REVIEW", "medium"},
        {"BLOCKED", "high"},
    }
    for _, tc := range cases {
        b, err := BuildBundle(Evidence{Endpoint: "/v1/orders", Method: "GET", Decision: tc.decision, Reasons: []string{"test"}, Remediations: []string{"identify consumer"}})
        if err != nil { t.Fatal(err) }
        if b.Priority != tc.want { t.Fatalf("%s: got %s want %s", tc.decision, b.Priority, tc.want) }
        if len(b.Actions) != 1 || b.Actions[0].Order != 1 { t.Fatalf("%s: invalid actions", tc.decision) }
    }
}
