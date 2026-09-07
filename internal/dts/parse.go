package dts

import (
	"bufio"
	"fmt"
	"regexp"
	"strconv"
	"strings"
)

// Evidence is intentionally small: it extracts stable, auditable facts from
// common DTS text without pretending to be a complete Device Tree compiler.
type Evidence struct {
	Source     string            `json:"source"`
	IOMMUCount int               `json:"iommu_count"`
	DMADevices int               `json:"dma_devices"`
	IOMMURefs  map[string]string `json:"iommu_refs"`
	Compatible []string          `json:"compatible"`
	Interrupts int               `json:"interrupts"`
}

var (
	nodeRE      = regexp.MustCompile(`(?m)^\s*([A-Za-z0-9,_@.+-]+)\s*\{`)
	compatRE    = regexp.MustCompile(`(?m)compatible\s*=\s*"([^"]+)"`)
	iommuRefRE  = regexp.MustCompile(`(?m)\biommus\s*=\s*<([^>]+)>\s*;`)
	interruptRE = regexp.MustCompile(`(?m)^\s*interrupts(?:-extended)?\s*=`)
)

func Parse(source, text string) (Evidence, error) {
	if strings.TrimSpace(text) == "" { return Evidence{}, fmt.Errorf("empty DTS source") }
	e := Evidence{Source: source, IOMMURefs: map[string]string{}}
	for _, m := range nodeRE.FindAllStringSubmatch(text, -1) {
		if strings.Contains(strings.ToLower(m[1]), "iommu") { e.IOMMUCount++ }
	}
	for _, m := range compatRE.FindAllStringSubmatch(text, -1) { e.Compatible = append(e.Compatible, m[1]) }
	for _, m := range iommuRefRE.FindAllStringSubmatch(text, -1) {
		if strings.TrimSpace(m[1]) != "" { e.DMADevices++ }
	}
	e.Interrupts = len(interruptRE.FindAllStringIndex(text, -1))
	return e, nil
}

// ParseUintCell converts a DTS cell such as 0x10 or 16 into an unsigned value.
func ParseUintCell(cell string) (uint64, error) {
	cell = strings.TrimSpace(strings.TrimSuffix(strings.TrimPrefix(cell, "<"), ">"))
	if cell == "" { return 0, fmt.Errorf("empty cell") }
	base := 10
	if strings.HasPrefix(cell, "0x") || strings.HasPrefix(cell, "0X") { base = 16; cell = cell[2:] }
	return strconv.ParseUint(cell, base, 64)
}

func ScanLines(text string) int {
	s := bufio.NewScanner(strings.NewReader(text)); n := 0
	for s.Scan() { if strings.TrimSpace(s.Text()) != "" { n++ } }
	return n
}
