package dts

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"

	"github.com/smokblack999-a11y/project-samurai/internal/audit"
)

// Parse extracts only evidence that can be identified conservatively from a
// Linux-style DTS source. It deliberately does not infer compliance from
// missing properties. The result is an audit.Target suitable for deterministic
// checks; unsupported constructs are left as unknown rather than guessed.
func Parse(sourceName, text string) (audit.Target, error) {
	clean := stripComments(text)
	if strings.TrimSpace(clean) == "" {
		return audit.Target{}, fmt.Errorf("empty DTS source")
	}

	t := audit.Target{SpecVersion: "1.0", EvidenceSource: sourceName}
	blocks := parseBlocks(clean)
	phandles := map[string]string{}

	for _, b := range blocks {
		if v, ok := b.props["phandle"]; ok {
			if h := firstCell(v); h != "" {
				phandles[h] = b.name
			}
		}
	}

	for _, b := range blocks {
		compatible := unquoteList(b.props["compatible"])
		if isIOMMUCompatible(compatible) {
			x := audit.IOMMU{Name: b.name, Enabled: !hasStatusDisabled(b.props["status"])}
			x.SpecSupported = boolPtrFromCompatible(compatible)
			if cells, ok := parseCells(b.props["#iommu-cells"]); ok && len(cells) > 0 {
				_ = cells // retained as presence evidence; width is not implied by #iommu-cells.
			}
			t.IOMMUs = append(t.IOMMUs, x)
		}
	}

	for _, b := range blocks {
		if isDisabled(b.props["status"]) {
			continue
		}
		if _, ok := b.props["dma-coherent"]; ok || hasDMACompatible(unquoteList(b.props["compatible"])) {
			d := audit.Device{Name: b.name, DMACapable: true, PCIe: isPCIeCompatible(unquoteList(b.props["compatible"]))}
			if v, ok := b.props["iommus"]; ok {
				if h := firstPhandle(v); h != "" {
					d.IOMMU = phandles[h]
				}
			}
			t.Devices = append(t.Devices, d)
		}
	}

	return t, nil
}

func stripComments(s string) string {
	re := regexp.MustCompile(`(?s)/\*.*?\*/|//[^\n]*`)
	return re.ReplaceAllString(s, "")
}

type block struct {
	name  string
	props map[string]string
}

func parseBlocks(s string) []block {
	var out []block
	for i := 0; i < len(s); {
		open := strings.IndexByte(s[i:], '{')
		if open < 0 {
			break
		}
		open += i
		semi := strings.LastIndex(s[i:open], ";")
		start := i
		if semi >= 0 {
			start = i + semi + 1
		}
		header := strings.TrimSpace(s[start:open])
		close := matchingBrace(s, open)
		if close < 0 {
			break
		}
		name := normalizeNodeName(header)
		if name != "" {
			out = append(out, block{name: name, props: parseProperties(s[open+1 : close])})
		}
		i = close + 1
	}
	return out
}

func matchingBrace(s string, open int) int {
	depth := 0
	for i := open; i < len(s); i++ {
		switch s[i] {
		case '{': depth++
		case '}':
			depth--
			if depth == 0 { return i }
		}
	}
	return -1
}

func normalizeNodeName(header string) string {
	header = strings.TrimSpace(header)
	if header == "" || strings.HasPrefix(header, "/") || strings.Contains(header, "=") {
		return ""
	}
	parts := strings.Fields(header)
	if len(parts) == 0 { return "" }
	name := parts[len(parts)-1]
	name = strings.TrimSpace(name)
	if idx := strings.IndexByte(name, '@'); idx >= 0 { name = name[:idx] }
	return strings.Trim(name, "<>")
}

func parseProperties(body string) map[string]string {
	props := map[string]string{}
	for _, stmt := range strings.Split(body, ";") {
		stmt = strings.TrimSpace(stmt)
		if stmt == "" || strings.Contains(stmt, "{") || strings.Contains(stmt, "}") { continue }
		if eq := strings.IndexByte(stmt, '='); eq >= 0 {
			key := strings.TrimSpace(stmt[:eq])
			val := strings.TrimSpace(stmt[eq+1:])
			props[key] = val
		} else {
			props[stmt] = ""
		}
	}
	return props
}

func unquoteList(v string) []string {
	var out []string
	re := regexp.MustCompile(`"([^"]+)"`)
	for _, m := range re.FindAllStringSubmatch(v, -1) { out = append(out, m[1]) }
	return out
}

func parseCells(v string) ([]uint64, bool) {
	m := regexp.MustCompile(`<([^>]+)>`).FindStringSubmatch(v)
	if len(m) < 2 { return nil, false }
	var out []uint64
	for _, tok := range strings.Fields(m[1]) {
		tok = strings.TrimPrefix(tok, "0x")
		n, err := strconv.ParseUint(tok, 16, 64)
		if err != nil { return nil, false }
		out = append(out, n)
	}
	return out, true
}

func firstCell(v string) string {
	m := regexp.MustCompile(`<([^>]+)>`).FindStringSubmatch(v)
	if len(m) < 2 { return "" }
	return strings.Fields(m[1])[0]
}

func firstPhandle(v string) string {
	m := regexp.MustCompile(`&([A-Za-z0-9_\-]+)`).FindStringSubmatch(v)
	if len(m) < 2 { return "" }
	return m[1]
}

func isIOMMUCompatible(xs []string) bool {
	for _, x := range xs {
		if strings.Contains(strings.ToLower(x), "iommu") { return true }
	}
	return false
}

func hasDMACompatible(xs []string) bool {
	for _, x := range xs {
		x = strings.ToLower(x)
		if strings.Contains(x, "dma") || strings.Contains(x, "nvme") || strings.Contains(x, "ethernet") || strings.Contains(x, "network") || strings.Contains(x, "gpu") { return true }
	}
	return false
}

func isPCIeCompatible(xs []string) bool {
	for _, x := range xs {
		if strings.Contains(strings.ToLower(x), "pcie") || strings.Contains(strings.ToLower(x), "pci") { return true }
	}
	return false
}

func isDisabled(v string) bool { return strings.Contains(strings.ToLower(v), "\"disabled\"") }
func hasStatusDisabled(v string) bool { return isDisabled(v) }

// DTS cannot prove RISC-V IOMMU spec support merely from a compatible string.
// Keep this unknown unless a future binding explicitly establishes it.
func boolPtrFromCompatible(_ []string) *bool { return nil }
