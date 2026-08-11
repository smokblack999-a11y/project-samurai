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
	jsonOut := flag.Bool("json", false, "emit machine-readable results")
	flag.Parse()
	if strings.TrimSpace(*input) == "" {
		fmt.Fprintln(os.Stderr, "usage: samurai-ci -input endpoint.json [-json]")
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

	blocked := false
	results := make([]lifecycle.RiskResult, 0, len(records))
	for _, endpoint := range records {
		if err := endpoint.Validate(); err != nil { fatal(fmt.Errorf("%s %s: %w", endpoint.Method, endpoint.Endpoint, err)) }
		result := risk.Evaluate(endpoint)
		results = append(results, result)
		if result.Decision == lifecycle.DecisionBlocked { blocked = true }
	}

	if *jsonOut {
		out, err := json.MarshalIndent(results, "", "  ")
		if err != nil { fatal(err) }
		fmt.Println(string(out))
	} else {
		for _, result := range results {
			fmt.Printf("[%s] score=%d confidence=%d\n", result.Decision, result.Score, result.Confidence)
		}
	}

	if blocked {
		fmt.Fprintln(os.Stderr, "API retirement gate: BLOCKED")
		os.Exit(1)
	}
	fmt.Fprintln(os.Stderr, "API retirement gate: PASS")
}

func fatal(err error) { fmt.Fprintln(os.Stderr, "error:", err); os.Exit(1) }
