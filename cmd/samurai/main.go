package main

import (
    "encoding/json"
    "flag"
    "fmt"
    "os"

    "github.com/smokblack999-a11y/project-samurai/internal/audit"
)

func main() {
    if len(os.Args) < 3 || os.Args[1] != "audit" {
        fmt.Fprintln(os.Stderr, "usage: samurai audit [--format json] [--fail-on high] target.json")
        os.Exit(2)
    }

    fs := flag.NewFlagSet("audit", flag.ExitOnError)
    format := fs.String("format", "text", "text|json")
    failOn := fs.String("fail-on", "critical", "critical|high|medium|low|none")
    _ = fs.Parse(os.Args[2:])
    if fs.NArg() != 1 {
        fmt.Fprintln(os.Stderr, "target.json is required")
        os.Exit(2)
    }

    data, err := os.ReadFile(fs.Arg(0))
    if err != nil { panic(err) }
    var target audit.Target
    if err := json.Unmarshal(data, &target); err != nil { panic(err) }

    findings := audit.Run(target)
    if *format == "json" {
        out := struct { Findings []audit.Finding `json:"findings"` }{findings}
        enc := json.NewEncoder(os.Stdout); enc.SetIndent("", "  "); _ = enc.Encode(out)
    } else {
        for _, f := range findings { fmt.Printf("[%s] %s: %s\n", f.Severity, f.Rule, f.Title) }
    }
    if audit.ShouldFail(findings, *failOn) { os.Exit(1) }
}
