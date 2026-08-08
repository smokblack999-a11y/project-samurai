package main

import (
	"flag"
	"fmt"
	"os"
	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/parser"
	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/risk"
	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/report"
)

func main() {
	input := flag.String("openapi", "", "OpenAPI JSON file")
	flag.Parse()
	if *input == "" { fmt.Fprintln(os.Stderr, "usage: samurai-lifecycle -openapi openapi.json"); os.Exit(2) }
	records, err := parser.LoadJSON(*input); if err != nil { fatal(err) }
	engine := risk.New()
	for _, r := range records { report.Print(r, engine.Evaluate(r)) }
}

func fatal(err error) { fmt.Fprintln(os.Stderr, "error:", err); os.Exit(1) }
