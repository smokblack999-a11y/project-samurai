package inventory

import (
    "strings"
    "testing"
)

func TestReadOpenAPI(t *testing.T) {
    input := `{"openapi":"3.0.3","paths":{"/v1/orders":{"get":{"operationId":"listOrders","deprecated":true},"post":{}},"/health":{"get":{}}}}`
    got, err := Read(strings.NewReader(input))
    if err != nil { t.Fatal(err) }
    if len(got) != 3 { t.Fatalf("got %d endpoints", len(got)) }
    if got[0].Path != "/health" || got[0].Method != "GET" { t.Fatalf("unexpected first endpoint: %+v", got[0]) }
    if !got[1].Deprecated || got[1].OperationID != "listOrders" { t.Fatalf("deprecated operation not preserved: %+v", got[1]) }
}

func TestReadRejectsNonOpenAPI(t *testing.T) {
    if _, err := Read(strings.NewReader(`{"hello":"world"}`)); err == nil { t.Fatal("expected validation error") }
}
