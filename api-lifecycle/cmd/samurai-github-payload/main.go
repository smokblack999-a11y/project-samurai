package main

import (
    "encoding/json"
    "flag"
    "fmt"
    "os"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/githubremediation"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
)

func main() {
    in := flag.String("in", "evidence.json", "audit evidence JSON")
    out := flag.String("out", "github-payload.json", "GitHub payload JSON")
    flag.Parse()
    raw, err := os.ReadFile(*in); if err != nil { panic(err) }
    var e report.Evidence
    if err := json.Unmarshal(raw, &e); err != nil { panic(err) }
    p, err := githubremediation.Build(e); if err != nil { panic(err) }
    encoded, err := json.MarshalIndent(p, "", "  "); if err != nil { panic(err) }
    if err := os.WriteFile(*out, encoded, 0644); err != nil { panic(err) }
    fmt.Printf("decision=%s fingerprint=%s output=%s\n", p.Decision, p.Fingerprint, *out)
}
