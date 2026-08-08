package report

import (
    "strings"
    "testing"
)

func TestRenderHTML(t *testing.T) {
    var b strings.Builder
    err := RenderHTML(&b, Evidence{Decision:"REVIEW", Method:"GET", Endpoint:"/v1/orders", ConsumerCount:2, ActiveConsumerCount:1, MigrationCompletion:0.5})
    if err != nil { t.Fatal(err) }
    if !strings.Contains(b.String(), "Decision: REVIEW") { t.Fatal("decision missing") }
    if !strings.Contains(b.String(), "GET /v1/orders") { t.Fatal("endpoint missing") }
}
