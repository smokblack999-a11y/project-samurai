package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"github.com/smokblack999-a11y/project-samurai/internal/audit"
	"github.com/smokblack999-a11y/project-samurai/internal/dts"
	"github.com/smokblack999-a11y/project-samurai/internal/regdump"
)

type sarifLog struct { Version string `json:"version"`; Schema string `json:"$schema"`; Runs []sarifRun `json:"runs"` }
type sarifRun struct { Tool sarifTool `json:"tool"`; Results []sarifResult `json:"results"` }
type sarifTool struct { Driver sarifDriver `json:"driver"` }
type sarifDriver struct { Name string `json:"name"`; Version string `json:"version"` }
type sarifResult struct { RuleID string `json:"ruleId"`; Level string `json:"level"`; Message sarifMessage `json:"message"`; Properties map[string]string `json:"properties,omitempty"` }
type sarifMessage struct { Text string `json:"text"` }

func main() {
	if len(os.Args) < 3 || (os.Args[1] != "audit" && os.Args[1] != "audit-dts" && os.Args[1] != "audit-regs") {
		fmt.Fprintln(os.Stderr, "usage: samurai audit [--format text|json|sarif] [--fail-on high] target.json")
		fmt.Fprintln(os.Stderr, "       samurai audit-dts [--format text|json] target.dts")
		fmt.Fprintln(os.Stderr, "       samurai audit-regs [--format text|json|sarif] [--fail-on high] dump.json")
		os.Exit(2)
	}
	fs := flag.NewFlagSet(os.Args[1], flag.ExitOnError)
	format := fs.String("format", "text", "text|json|sarif")
	failOn := fs.String("fail-on", "critical", "critical|high|medium|low|none")
	_ = fs.Parse(os.Args[2:])
	if fs.NArg() != 1 { fmt.Fprintln(os.Stderr, "input file is required"); os.Exit(2) }
	data, err := os.ReadFile(fs.Arg(0))
	if err != nil { fmt.Fprintln(os.Stderr, err); os.Exit(2) }

	if os.Args[1] == "audit-dts" {
		target, err := dts.Parse(fs.Arg(0), string(data))
		if err != nil { fmt.Fprintln(os.Stderr, err); os.Exit(2) }
		out := struct { Source string `json:"source"`; IOMMUCount int `json:"iommu_count"`; DMADevices int `json:"dma_devices"`; Interrupts int `json:"interrupts"`; Target audit.Target `json:"target"` }{target.EvidenceSource, len(target.IOMMUs), len(target.Devices), dts.InterruptCount(string(data)), target}
		switch *format {
		case "json": enc := json.NewEncoder(os.Stdout); enc.SetIndent("", "  "); _ = enc.Encode(out)
		case "text": fmt.Printf("source=%s iommu_nodes=%d dma_references=%d interrupts=%d\n", out.Source, out.IOMMUCount, out.DMADevices, out.Interrupts)
		default: fmt.Fprintln(os.Stderr, "audit-dts supports text or json"); os.Exit(2)
		}
		return
	}

	var target audit.Target
	if os.Args[1] == "audit-regs" {
		dump, err := regdump.Load(fs.Arg(0)); if err != nil { fmt.Fprintln(os.Stderr, err); os.Exit(2) }
		target = regdump.ToTarget(dump)
	} else if err := json.Unmarshal(data, &target); err != nil { fmt.Fprintln(os.Stderr, err); os.Exit(2) }

	findings := audit.Run(target)
	switch *format {
	case "json":
		out := struct { Findings []audit.Finding `json:"findings"`; Target audit.Target `json:"target"` }{findings, target}
		enc := json.NewEncoder(os.Stdout); enc.SetIndent("", "  "); _ = enc.Encode(out)
	case "sarif":
		results := make([]sarifResult, 0, len(findings))
		for _, f := range findings { level := "warning"; if f.Severity == audit.Critical || f.Severity == audit.High { level = "error" }; results = append(results, sarifResult{RuleID:f.Rule, Level:level, Message:sarifMessage{Text:f.Title+": "+f.Evidence}, Properties:map[string]string{"severity":string(f.Severity), "normative_level":string(f.NormativeLevel), "confidence":f.Confidence, "spec":f.Spec, "remediation":f.Remediation}}) }
		out := sarifLog{Version:"2.1.0", Schema:"https://json.schemastore.org/sarif-2.1.0.json", Runs:[]sarifRun{{Tool:sarifTool{Driver:sarifDriver{Name:"SamuraiOS", Version:"0.1.0"}}, Results:results}}}
		enc := json.NewEncoder(os.Stdout); enc.SetIndent("", "  "); _ = enc.Encode(out)
	case "text":
		for _, f := range findings { fmt.Printf("[%s] %s (%s/%s): %s\n", f.Severity, f.Rule, f.NormativeLevel, f.Confidence, f.Title) }
	default: fmt.Fprintln(os.Stderr, "invalid --format: use text, json or sarif"); os.Exit(2)
	}
	if audit.ShouldFail(findings, *failOn) { os.Exit(1) }
}
