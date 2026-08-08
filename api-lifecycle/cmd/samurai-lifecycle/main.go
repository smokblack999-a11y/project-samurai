package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/model"
	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/risk"
)

func main() {
	input := flag.String("input", "", "path to a lifecycle JSON record")
	flag.Parse()
	if *input == "" {
		fmt.Fprintln(os.Stderr, "usage: samurai-lifecycle -input endpoint.json")
		os.Exit(2)
	}
	data, err := os.ReadFile(*input)
	if err != nil { fatal(err) }
	var endpoint model.LifecycleRecord
	if err := json.Unmarshal(data, &endpoint); err != nil { fatal(err) }
	result := risk.New().Evaluate(endpoint)
	out, err := json.MarshalIndent(result, "", "  ")
	if err != nil { fatal(err) }
	fmt.Println(string(out))
}

func fatal(err error) { fmt.Fprintln(os.Stderr, "error:", err); os.Exit(1) }
