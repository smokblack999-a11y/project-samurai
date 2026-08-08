package spec

import (
    "encoding/json"
    "fmt"
    "io"
    "strings"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

type Document struct { Paths map[string]PathItem `json:"paths"` }
type PathItem struct {
    Get *Operation `json:"get"`; Post *Operation `json:"post"`; Put *Operation `json:"put"`; Patch *Operation `json:"patch"`; Delete *Operation `json:"delete"`; Head *Operation `json:"head"`; Options *Operation `json:"options"`
}
type Operation struct { OperationID string `json:"operationId"`; Deprecated bool `json:"deprecated"` }

func Read(r io.Reader) ([]lifecycle.Endpoint, error) {
    var d Document
    if err:=json.NewDecoder(r).Decode(&d); err!=nil{return nil,err}
    var out []lifecycle.Endpoint
    for path,item := range d.Paths {
        methods := []struct{name string; op *Operation}{
            {"GET",item.Get},{"POST",item.Post},{"PUT",item.Put},{"PATCH",item.Patch},{"DELETE",item.Delete},{"HEAD",item.Head},{"OPTIONS",item.Options},
        }
        for _,m := range methods {
            if m.op == nil { continue }
            status := lifecycle.StatusActive
            if m.op.Deprecated { status = lifecycle.StatusDeprecated }
            out = append(out, lifecycle.Endpoint{Endpoint:path, Method:m.name, Status:status})
        }
    }
    if len(out)==0{return nil,fmt.Errorf("openapi document contains no operations")}
    return out,nil
}

func MethodPath(method,path string) string { return strings.ToUpper(method)+" "+path }
