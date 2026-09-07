package regdump

import "testing"

func TestToTargetPreservesUnknowns(t *testing.T) {
	d := Dump{Source: "capture.txt", IOMMUs: []IOMMUDump{{Name: "iommu0", Enabled: ptr(true), PhysAddrBits: ptr(48)}}}
	target := ToTarget(d)
	if target.EvidenceSource != "capture.txt" { t.Fatal("evidence source lost") }
	if len(target.IOMMUs) != 1 || target.IOMMUs[0].PhysAddrBits != 48 { t.Fatal("register evidence not mapped") }
	if target.IOMMUs[0].MSI { t.Fatal("unknown MSI must not become true") }
}

func ptr[T any](v T) *T { return &v }
