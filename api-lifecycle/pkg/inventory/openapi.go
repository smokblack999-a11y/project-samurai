package inventory

import (
    "encoding/json"
    "fmt"
    "io"
    "sort"
    "strings"
)

type Endpoint struct {
    Method string `json:"method"`
    Path string `json:"path"`
    OperationID string `json:"operation_id,omitempty"`
    Deprecated bool `json:"deprecated"`
}

type document struct {
    OpenAPI string `json:"openapi"`
    Swagger string `json:"swagger"`
    Paths map[string]map[string]operation `json:"paths"`
}

type operation struct {
    OperationID string `json:"operationId"`
    Deprecated *bool `json:"deprecated"`
}

var methods = map[string]bool{"get":true,"post":true,"put":true,"patch":true,"delete":true,"head":true,"options":true,"trace":true}

func Read(r io.Reader) ([]Endpoint, error) {
    var doc document
    if err := json.NewDecoder(r).Decode(&doc); err != nil { return nil, fmt.Errorf("decode OpenAPI: %w", err) }
    if doc.OpenAPI == "" && doc.Swagger == "" { return nil, fmt.Errorf("not an OpenAPI/Swagger document") }
    if len(doc.Paths) == 0 { return []Endpoint{}, nil }

    out := make([]Endpoint, 0)
    for path, ops := range doc.Paths {
        if !strings.HasPrefix(path, "/") { return nil, fmt.Errorf("invalid path %q", path) }
        for method, op := range ops {
            m := strings.ToLower(method)
            if !methods[m] { continue }
            deprecated := op.Deprecated != nil && *op.Deprecated
            out = append(out, Endpoint{Method: strings.ToUpper(m), Path: path, OperationID: op.OperationID, Deprecated: deprecated})
        }
    }
    sort.Slice(out, func(i,j int) bool { if out[i].Path == out[j].Path { return out[i].Method < out[j].Method }; return out[i].Path < out[j].Path })
    return out, nil
}
