package regdump

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/smokblack999-a11y/project-samurai/internal/audit"
)

// Dump is a conservative normalized representation of evidence extracted from
// an MMIO/register capture. Missing MUST-level evidence is rejected before the
// deterministic audit runs; the adapter never invents compliance values.
type Dump struct {
	Source string `json:"source"`
	IOMMUs []IOMMUDump `json:"iommus"`
}

type IOMMUDump struct {
	Name string `json:"name"`
	Enabled *bool `json:"enabled,omitempty"`
	SpecSupported *bool `json:"spec_supported,omitempty"`
	DeviceIDBits *int `json:"device_id_bits,omitempty"`
	PhysAddrBits *int `json:"phys_addr_bits,omitempty"`
	ATS *bool `json:"ats,omitempty"`
	T2GPA *bool `json:"t2gpa,omitempty"`
	MSI *bool `json:"msi,omitempty"`
	ResetMode *string `json:"reset_mode,omitempty"`
	PMPEnforced *bool `json:"pmp_enforced,omitempty"`
	PASIDSupported *bool `json:"pasid_supported,omitempty"`
	PASIDBits *int `json:"pasid_bits,omitempty"`
}

func Load(path string) (Dump, error) {
	data, err := os.ReadFile(path)
	if err != nil { return Dump{}, err }
	var d Dump
	if err := json.Unmarshal(data, &d); err != nil { return Dump{}, fmt.Errorf("register dump: %w", err) }
	if len(d.IOMMUs) == 0 { return Dump{}, fmt.Errorf("register dump: no IOMMU records") }
	if err := d.Validate(); err != nil { return Dump{}, err }
	return d, nil
}

// Validate ensures every field needed for a MUST-level rule represented by
// this adapter is actually present. SHOULD-level fields remain optional.
func (d Dump) Validate() error {
	for _, r := range d.IOMMUs {
		missing := ""
		if r.Name == "" { missing += " name" }
		if r.Enabled == nil { missing += " enabled" }
		if r.DeviceIDBits == nil { missing += " device_id_bits" }
		if r.PhysAddrBits == nil { missing += " phys_addr_bits" }
		if r.MSI == nil { missing += " msi" }
		if r.ResetMode == nil { missing += " reset_mode" }
		if r.PMPEnforced == nil { missing += " pmp_enforced" }
		if r.PASIDSupported == nil { missing += " pasid_supported" }
		if r.PASIDSupported != nil && *r.PASIDSupported && r.PASIDBits == nil { missing += " pasid_bits" }
		if missing != "" { return fmt.Errorf("register evidence incomplete for %q; missing MUST-level fields:%s", r.Name, missing) }
	}
	return nil
}

func ToTarget(d Dump) audit.Target {
	t := audit.Target{SpecVersion: "1.0", EvidenceSource: d.Source}
	for _, r := range d.IOMMUs {
		x := audit.IOMMU{Name: r.Name}
		if r.Enabled != nil { x.Enabled = *r.Enabled }
		x.SpecSupported = r.SpecSupported
		if r.DeviceIDBits != nil { x.DeviceIDBits = *r.DeviceIDBits }
		if r.PhysAddrBits != nil { x.PhysAddrBits = *r.PhysAddrBits }
		if r.ATS != nil { x.ATS = *r.ATS }
		if r.T2GPA != nil { x.T2GPA = *r.T2GPA }
		if r.MSI != nil { x.MSI = *r.MSI }
		if r.ResetMode != nil { x.ResetMode = *r.ResetMode }
		if r.PMPEnforced != nil { x.PMPEnforced = *r.PMPEnforced }
		if r.PASIDSupported != nil { x.PASIDSupported = *r.PASIDSupported }
		if r.PASIDBits != nil { x.PASIDBits = *r.PASIDBits }
		t.IOMMUs = append(t.IOMMUs, x)
	}
	return t
}
