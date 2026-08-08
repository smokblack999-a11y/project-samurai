package spec

import (
    "strings"
    "testing"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

func TestReadMapsDeprecatedOperation(t *testing.T) {
    doc := `{"openapi":"3.1.0","paths":{"/v1/orders":{"get":{"operationId":"listOrders","deprecated":true},"post":{"operationId":"createOrder"}}}}`
    got, err := Read(strings.NewReader(doc))
    if err != nil { t.Fatal(err) }
    if len(got) != 2 { t.Fatalf("got %d endpoints", len(got)) }
    if got[0].Method != "GET" || got[0].Status != lifecycle.StatusDeprecated { t.Fatalf("unexpected endpoint: %+v", got[0]) }
}
