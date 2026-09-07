package dts

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"

	"github.com/smokblack999-a11y/project-samurai/internal/audit"
)

// Parse extracts only evidence that can be identified conservatively from a
// Linux-style DTS source. Missing properties remain unknown rather than guessed.
func Parse(sourceName, text string) (audit.Target, error) {
	clean := stripComments(text)
	if strings.TrimSpace(clean) == "" { return audit.Target{}, fmt.Errorf("empty DTS source") }
	t := audit.Target{SpecVersion: "1.0", EvidenceSource: sourceName}
	blocks := parseBlocks(clean)
	phandles := map[string]string{}
	for _, b := range blocks {
		if v, ok := b.props["phandle"]; ok { if h := firstCell(v); h != "" { phandles[h] = b.name } }
	}
	for _, b := range blocks {
		compatible := unquoteList(b.props["compatible"])
		if isIOMMUCompatible(compatible) {
			x := audit.IOMMU{Name: b.name, Enabled: !hasStatusDisabled(b.props["status"])}
			x.SpecSupported = boolPtrFromCompatible(compatible)
			t.IOMMUs = append(t.IOMMUs, x)
		}
	}
	for _, b := range blocks {
		if isDisabled(b.props["status"]) { continue }
		// An explicit iommus property is direct evidence that the node participates
		// in IOMMU-governed DMA, even when its compatible string is vendor-specific.
		_, hasIOMMURef := b.props["iommus"]
		if _, coherent := b.props["dma-coherent"]; coherent || hasIOMMURef || hasDMACompatible(unquoteList(b.props["compatible"])) {
			d := audit.Device{Name: b.name, DMACapable: true, PCIe: isPCIeCompatible(unquoteList(b.props["compatible"]))}
			if v, ok := b.props["iommus"]; ok { if h := firstPhandle(v); h != "" { d.IOMMU = phandles[h] } }
			t.Devices = append(t.Devices, d)
		}
	}
	return t, nil
}

// InterruptCount returns the number of explicit interrupt properties in the
// parsed DTS blocks. It is evidence extraction only; it makes no compliance claim.
func InterruptCount(text string) int {
	clean := stripComments(text)
	count := 0
	for _, b := range parseBlocks(clean) { if _, ok := b.props["interrupts"]; ok { count++ } }
	return count
}

func stripComments(s string) string {
	re := regexp.MustCompile(`(?s)/\*.*?\*/|//[^\n]*`)
	return re.ReplaceAllString(s, "")
}

type block struct { name string; props map[string]string }

func parseBlocks(s string) []block {
	var out []block
	for i := 0; i < len(s); {
		open := strings.IndexByte(s[i:], '{'); if open < 0 { break }; open += i
		semi := strings.LastIndex(s[i:open], ";"); start := i; if semi >= 0 { start = i + semi + 1 }
		header := strings.TrimSpace(s[start:open]); close := matchingBrace(s, open); if close < 0 { break }
		name := normalizeNodeName(header); if name != "" { out = append(out, block{name:name, props:parseProperties(s[open+1:close])}) }
		i = close + 1
	}
	return out
}

func matchingBrace(s string, open int) int {
	depth := 0
	for i := open; i < len(s); i++ { switch s[i] { case '{': depth++; case '}': depth--; if depth == 0 { return i } } }
	return -1
}

func normalizeNodeName(header string) string {
	header = strings.TrimSpace(header); if header == "" || strings.HasPrefix(header, "/") || strings.Contains(header, "=") { return "" }
	parts := strings.Fields(header); if len(parts) == 0 { return "" }; name := parts[len(parts)-1]
	if idx := strings.IndexByte(name, '@'); idx >= 0 { name = name[:idx] }
	return strings.Trim(name, "<>")
}

func parseProperties(body string) map[string]string {
	props := map[string]string{}
	for _, stmt := range strings.Split(body, ";") {
		stmt = strings.TrimSpace(stmt); if stmt == "" || strings.Contains(stmt, "{") || strings.Contains(stmt, "}") { continue }
		if eq := strings.IndexByte(stmt, '='); eq >= 0 { props[strings.TrimSpace(stmt[:eq])] = strings.TrimSpace(stmt[eq+1:]) } else { props[stmt] = "" }
	}
	return props
}

func unquoteList(v string) []string {
	var out []string; re := regexp.MustCompile(`"([^"]+)"`)
	for _, m := range re.FindAllStringSubmatch(v, -1) { out = append(out, m[1]) }
	return out
}

func parseCells(v string) ([]uint64, bool) {
	m := regexp.MustCompile(`<([^>]+)>`).FindStringSubmatch(v); if len(m) < 2 { return nil, false }
	var out []uint64
	for _, tok := range strings.Fields(m[1]) { tok = strings.TrimPrefix(tok, "0x"); n, err := strconv.ParseUint(tok, 16, 64); if err != nil { return nil, false }; out = append(out, n) }
	return out, true
}

func firstCell(v string) string { m := regexp.MustCompile(`<([^>]+)>`).FindStringSubmatch(v); if len(m) < 2 { return "" }; return strings.Fields(m[1])[0] }
func firstPhandle(v string) string { m := regexp.MustCompile(`&([A-Za-z0-9_\-]+)`).FindStringSubmatch(v); if len(m) < 2 { return "" }; return m[1] }
func isIOMMUCompatible(xs []string) bool { for _, x := range xs { if strings.Contains(strings.ToLower(x), "iommu") { return true } }; return false }
func hasDMACompatible(xs []string) bool { for _, x := range xs { x = strings.ToLower(x); if strings.Contains(x, "dma") || strings.Contains(x, "nvme") || strings.Contains(x, "ethernet") || strings.Contains(x, "network") || strings.Contains(x, "gpu") { return true } }; return false }
func isPCIeCompatible(xs []string) bool { for _, x := range xs { x = strings.ToLower(x); if strings.Contains(x, "pcie") || strings.Contains(x, "pci") { return true } }; return false }
func isDisabled(v string) bool { return strings.Contains(strings.ToLower(v), "\"disabled\"") }
func hasStatusDisabled(v string) bool { return isDisabled(v) }
func boolPtrFromCompatible(_ []string) *bool { return nil }
