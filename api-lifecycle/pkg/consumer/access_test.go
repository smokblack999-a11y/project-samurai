package consumer

import (
    "strings"
    "testing"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

func TestAttribute(t *testing.T) {
    records := []AccessRecord{
        {Method:"GET", Path:"/v1/orders", Consumer:"billing", Requests:9},
        {Method:"GET", Path:"/v1/orders", Consumer:"", Requests:1},
    }
    got := Attribute(lifecycle.Endpoint{Method:"GET", Endpoint:"/v1/orders"}, records)
    if got.ConsumerCount != 1 || got.ActiveConsumerCount != 1 { t.Fatalf("unexpected attribution: %+v", got) }
    if got.UnknownTrafficShare != 0.1 { t.Fatalf("unknown share=%v", got.UnknownTrafficShare) }
}

func TestReadJSONL(t *testing.T) {
    got, err := ReadJSONL(strings.NewReader(`{"method":"GET","path":"/x","consumer":"a"}
{"method":"POST","path":"/x","consumer":"b","requests":2}
`))
    if err != nil || len(got) != 2 { t.Fatalf("records=%v err=%v", got, err) }
    if got[0].Requests != 1 { t.Fatalf("default requests=%d", got[0].Requests) }
}
