package main

import (
    "encoding/json"
    "flag"
    "fmt"
    "os"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/remediation"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
)

func main() {
    in := flag.String("in", "", "audit evidence JSON")
    out := flag.String("out", "", "optional remediation bundle JSON")
    flag.Parse()
    if *in == "" { panic("usage: samurai-bundle -in evidence.json [-out bundle.json]") }
    data, err := os.ReadFile(*in); if err != nil { panic(err) }
    var evidence report.Evidence
    if err := json.Unmarshal(data, &evidence); err != nil { panic(err) }
    bundle, err := remediation.Build(evidence); if err != nil { panic(err) }
    encoded, err := remediation.Marshal(bundle); if err != nil { panic(err) }
    if *out != "" { if err := os.WriteFile(*out, encoded, 0644); err != nil { panic(err) }; fmt.Println(*out); return }
    fmt.Println(string(encoded))
}
