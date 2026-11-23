package regdump

import "testing"

func TestToTargetPreservesUnknowns(t *testing.T) {
	d := Dump{Source: "capture.txt", IOMMUs: []IOMMUDump{{Name: "iommu0", Enabled: ptr(true), PhysAddrBits: ptr(48)}}}
	target := ToTarget(d)
	if target.EvidenceSource != "capture.txt" { t.Fatal("evidence source lost") }
	if len(target.IOMMUs) != 1 || target.IOMMUs[0].PhysAddrBits != 48 { t.Fatal("register evidence not mapped") }
	if target.IOMMUs[0].MSI { t.Fatal("unknown MSI must not become true") }
}

func TestValidateAcceptsMUSTEvidence(t *testing.T) {
	d := Dump{IOMMUs: []IOMMUDump{{Name: "i0", Enabled: ptr(true), DeviceIDBits: ptr(16), PhysAddrBits: ptr(48), MSI: ptr(true), ResetMode: ptr("Off"), PMPEnforced: ptr(true), PASIDSupported: ptr(false)}}}
	if err := d.Validate(); err != nil { t.Fatal(err) }
}

func TestValidateRejectsMissingMUSTEvidence(t *testing.T) {
	d := Dump{IOMMUs: []IOMMUDump{{Name: "i0", Enabled: ptr(true), DeviceIDBits: ptr(16), PhysAddrBits: ptr(48), ResetMode: ptr("Off"), PMPEnforced: ptr(true), PASIDSupported: ptr(false)}}}
	if err := d.Validate(); err == nil { t.Fatal("expected missing MSI evidence to be rejected") }
}

func TestValidateRequiresPASIDWidthWhenSupported(t *testing.T) {
	d := Dump{IOMMUs: []IOMMUDump{{Name: "i0", Enabled: ptr(true), DeviceIDBits: ptr(16), PhysAddrBits: ptr(48), MSI: ptr(true), ResetMode: ptr("Off"), PMPEnforced: ptr(true), PASIDSupported: ptr(true)}}}
	if err := d.Validate(); err == nil { t.Fatal("expected missing PASID width to be rejected") }
}

func ptr[T any](v T) *T { return &v }
