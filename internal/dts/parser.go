package dts

import (
	"bufio"
	"fmt"
	"io"
	"regexp"
	"strconv"
	"strings"
)

// Node is a deliberately small device-tree representation. It preserves node
// names, compatible strings, status and raw properties needed by the first
// IOMMU evidence adapter without pretending to be a full DTB implementation.
type Node struct {
	Name       string
	Compatible []string
	Status     string
	Properties map[string]string
}

var nodeRE = regexp.MustCompile(`^\s*([A-Za-z0-9,._+@/-]+)\s*\{`)
var propRE = regexp.MustCompile(`^\s*([A-Za-z0-9,._+?#/-]+)\s*=\s*(.*);\s*$`)

func Parse(r io.Reader) ([]Node, error) {
	s := bufio.NewScanner(r)
	var out []Node
	var cur *Node
	depth := 0
	line := 0
	for s.Scan() {
		line++
		x := strings.TrimSpace(strings.SplitN(s.Text(), "//", 2)[0])
		if x == "" || strings.HasPrefix(x, "/dts-v1/") || x == "/plugin/;" || x == "/ {" { if x == "/ {" { depth++ }; continue }
		if m := nodeRE.FindStringSubmatch(x); m != nil {
			if cur != nil { return nil, fmt.Errorf("nested node unsupported at line %d", line) }
			cur = &Node{Name: m[1], Properties: map[string]string{}}
			depth++
			continue
		}
		if x == "};" || x == "}" {
			if cur != nil {
				out = append(out, *cur)
				cur = nil
			}
			if depth > 0 { depth-- }
			continue
		}
		if cur == nil { continue }
		if m := propRE.FindStringSubmatch(x); m != nil {
			key, value := m[1], strings.TrimSpace(m[2])
			cur.Properties[key] = value
			switch key {
			case "compatible": cur.Compatible = parseStrings(value)
			case "status": cur.Status = firstString(value)
			}
		}
	}
	if err := s.Err(); err != nil { return nil, err }
	if cur != nil { return nil, fmt.Errorf("unterminated node %q", cur.Name) }
	return out, nil
}

func parseStrings(v string) []string {
	v = strings.TrimSpace(v)
	if !strings.HasPrefix(v, "\"") { return nil }
	parts := strings.Split(v, "\"")
	var out []string
	for i := 1; i < len(parts); i += 2 { if parts[i] != "" { out = append(out, parts[i]) } }
	return out
}

func firstString(v string) string {
	x := parseStrings(v)
	if len(x) == 0 { return "" }
	return x[0]
}

func U32(value string) (uint32, error) {
	value = strings.TrimSpace(value)
	value = strings.TrimPrefix(value, "<")
	value = strings.TrimSuffix(value, ">")
	value = strings.TrimSpace(value)
	if strings.HasPrefix(value, "0x") || strings.HasPrefix(value, "0X") { n, err := strconv.ParseUint(value[2:], 16, 32); return uint32(n), err }
	return 0, fmt.Errorf("unsupported numeric value %q", value)
}
