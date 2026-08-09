package main

import (
    "encoding/json"
    "flag"
    "fmt"
    "os"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/audit"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/consumer"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/risk"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/spec"
)

func main() {
    openapi := flag.String("openapi", "", "OpenAPI JSON file")
    logs := flag.String("logs", "", "access log JSONL file")
    endpoint := flag.String("endpoint", "", "endpoint to audit")
    method := flag.String("method", "GET", "HTTP method")
    out := flag.String("out", "", "optional JSON evidence output")
    flag.Parse()
    if *openapi == "" || *logs == "" || *endpoint == "" { panic("usage: samurai-e2e -openapi FILE -logs FILE -endpoint PATH [-method GET] [-out FILE]") }

    f, err := os.Open(*openapi); if err != nil { panic(err) }; defer f.Close()
    endpoints, err := spec.Read(f); if err != nil { panic(err) }
    var epFound bool
    var ep = endpoints[0]
    for _, e := range endpoints { if e.Endpoint == *endpoint && e.Method == *method { ep=e; epFound=true; break } }
    if !epFound { panic(fmt.Sprintf("endpoint not found: %s %s", *method, *endpoint)) }

    lf, err := os.Open(*logs); if err != nil { panic(err) }; defer lf.Close()
    records, err := consumer.ReadJSONL(lf); if err != nil { panic(err) }

    evidence := audit.Run(audit.Input{Endpoint: ep, Records: records, Replacement: ep.Replacement, ReplacementHealthy: ep.ReplacementHealthy, MigrationCompletion: ep.MigrationCompletion, Policy: risk.DefaultPolicy()})
    if *out != "" { b, err := json.MarshalIndent(evidence, "", "  "); if err != nil { panic(err) }; if err:=os.WriteFile(*out,b,0644); err!=nil { panic(err) } }
    if err := report.RenderHTML(os.Stdout, evidence); err != nil { panic(err) }
}
