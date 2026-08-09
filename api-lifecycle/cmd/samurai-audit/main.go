package main

import (
    "flag"
    "fmt"
    "os"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/audit"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/consumer"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/risk"
)

func main() {
    input := flag.String("input", "examples/access-log.jsonl", "JSONL access log")
    endpoint := flag.String("endpoint", "/v1/orders", "endpoint path")
    method := flag.String("method", "GET", "HTTP method")
    replacement := flag.String("replacement", "/v2/orders", "replacement endpoint")
    healthy := flag.Bool("replacement-healthy", true, "replacement health status")
    migration := flag.Float64("migration", 1, "migration completion 0..1")
    format := flag.String("format", "json", "output format: json|html")
    output := flag.String("output", "", "output file; stdout when empty")
    flag.Parse()

    f, err := os.Open(*input)
    if err != nil { fatal(err) }
    defer f.Close()
    records, err := consumer.ReadJSONL(f)
    if err != nil { fatal(err) }

    evidence := audit.Run(audit.Input{
        Endpoint: lifecycle.Endpoint{Endpoint: *endpoint, Method: *method},
        Records: records,
        Replacement: *replacement,
        ReplacementHealthy: *healthy,
        MigrationCompletion: *migration,
        Policy: risk.DefaultPolicy,
    })

    var writer = os.Stdout
    if *output != "" {
        writer, err = os.Create(*output)
        if err != nil { fatal(err) }
        defer writer.Close()
    }

    switch *format {
    case "json":
        out, err := report.Marshal(evidence)
        if err != nil { fatal(err) }
        if _, err = writer.Write(append(out, '\n')); err != nil { fatal(err) }
    case "html":
        if err := report.RenderHTML(writer, evidence); err != nil { fatal(err) }
    default:
        fatal(fmt.Errorf("unsupported format %q; use json or html", *format))
    }

    fingerprint, err := report.Fingerprint(evidence)
    if err != nil { fatal(err) }
    fmt.Fprintf(os.Stderr, "audit decision=%s fingerprint=%s\n", evidence.Decision, fingerprint)
}

func fatal(err error) { fmt.Fprintln(os.Stderr, "audit error:", err); os.Exit(1) }
