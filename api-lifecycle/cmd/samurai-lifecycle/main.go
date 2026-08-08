package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"

	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/risk"
)

func main() {
	input := flag.String("input", "", "path to a lifecycle JSON object or array")
	jsonOut := flag.Bool("json", false, "emit machine-readable JSON")
	flag.Parse()
	if strings.TrimSpace(*input) == "" {
		fmt.Fprintln(os.Stderr, "usage: samurai-lifecycle -input endpoint.json [-json]")
		os.Exit(2)
	}
	data, err := os.ReadFile(*input)
	if err != nil { fatal(err) }

	var records []lifecycle.Endpoint
	if err := json.Unmarshal(data, &records); err != nil {
		var one lifecycle.Endpoint
		if err := json.Unmarshal(data, &one); err != nil { fatal(err) }
		records = []lifecycle.Endpoint{one}
	}

	results := make([]lifecycle.RiskResult, 0, len(records))
	for _, endpoint := range records {
		if err := endpoint.Validate(); err != nil { fatal(fmt.Errorf("%s %s: %w", endpoint.Method, endpoint.Endpoint, err)) }
		results = append(results, risk.Evaluate(endpoint))
	}

	if *jsonOut {
		out, err := json.MarshalIndent(results, "", "  ")
		if err != nil { fatal(err) }
		fmt.Println(string(out))
		return
	}

	for i, result := range results {
		fmt.Printf("[%s] score=%d confidence=%d\n", result.Decision, result.Score, result.Confidence)
		for _, reason := range result.Reasons { fmt.Printf("  - %s\n", reason) }
		for _, remediation := range result.Remediations { fmt.Printf("  -> %s\n", remediation) }
		if i < len(results)-1 { fmt.Println() }
	}
}

func fatal(err error) { fmt.Fprintln(os.Stderr, "error:", err); os.Exit(1) }
