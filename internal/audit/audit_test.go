package audit

import "testing"

func boolPtr(v bool) *bool { return &v }

func TestCleanTargetHasNoFindings(t *testing.T) {
	target := Target{
		SpecVersion: "1.0", CPUPhysAddrBits: 48,
		IOMMUs: []IOMMU{{Name: "iommu0", Enabled: true, DeviceIDBits: 16, PhysAddrBits: 48, ATS: true, T2GPA: true, MSI: true, ResetMode: "Off", PMPEnforced: true}},
		Devices: []Device{{Name: "nvme0", DMACapable: true, IOMMU: "iommu0", DeviceID: 42}},
	}
	if got := Run(target); len(got) != 0 { t.Fatalf("expected no findings, got %d: %#v", len(got), got) }
}

func TestRootPortRulesUse030AndNot040(t *testing.T) {
	target := Target{SpecVersion: "1.0", CPUPhysAddrBits: 48, IOMMUs: []IOMMU{{Name: "iommu0", Enabled: true, DeviceIDBits: 8, PhysAddrBits: 48, MSI: true, ResetMode: "Off", PMPEnforced: true}}, PCIeRootPorts: []PCIeRootPort{{Name: "rp0", IOMMU: "iommu0", Accessible: true}}}
	findings := Run(target)
	if len(findings) != 1 || findings[0].Rule != "IOM_030" { t.Fatalf("expected exactly IOM_030, got %#v", findings) }
}

func TestPASIDUsesIOM170(t *testing.T) {
	target := Target{SpecVersion: "1.0", CPUPhysAddrBits: 48, IOMMUs: []IOMMU{{Name: "iommu0", Enabled: true, DeviceIDBits: 16, PhysAddrBits: 48, MSI: true, ResetMode: "Off", PMPEnforced: true, PASIDSupported: true, PASIDBits: 17}}}
	findings := Run(target)
	if len(findings) != 1 || findings[0].Rule != "IOM_170" || findings[0].NormativeLevel != Must { t.Fatalf("expected MUST IOM_170 finding, got %#v", findings) }
}

func TestUnsupportedPASIDDoesNotCreateIOM170(t *testing.T) {
	target := Target{CPUPhysAddrBits: 48, IOMMUs: []IOMMU{{Name: "iommu0", Enabled: true, DeviceIDBits: 16, PhysAddrBits: 48, MSI: true, ResetMode: "Off", PMPEnforced: true, PASIDSupported: false, PASIDBits: 0}}}
	for _, f := range Run(target) { if f.Rule == "IOM_170" { t.Fatalf("unexpected IOM_170: %#v", f) } }
}

func TestShouldRulesDoNotFailHighGate(t *testing.T) {
	findings := []Finding{{Rule: "IOM_090", Severity: Low, NormativeLevel: Should}}
	if ShouldFail(findings, "high") { t.Fatal("SHOULD/advisory finding must not trip high security gate") }
}

func TestCriticalFindingTripsHighGate(t *testing.T) {
	findings := []Finding{{Rule: "IOM_260", Severity: Critical, NormativeLevel: Must}}
	if !ShouldFail(findings, "high") { t.Fatal("critical MUST finding must trip high security gate") }
}

func TestExplicitUnsupportedSpecTriggersIOM010(t *testing.T) {
	target := Target{IOMMUs: []IOMMU{{Name: "iommu0", SpecSupported: boolPtr(false), Enabled: true}}}
	found := false
	for _, f := range Run(target) { if f.Rule == "IOM_010" { found = true } }
	if !found { t.Fatalf("expected IOM_010 finding") }
}

func TestMissingHostBridgeEvidenceDoesNotCreateFalseFailure(t *testing.T) {
	target := Target{CPUPhysAddrBits: 48, IOMMUs: []IOMMU{{Name: "iommu0", Enabled: true, DeviceIDBits: 16, PhysAddrBits: 48, MSI: true, ResetMode: "Off", PMPEnforced: true}}}
	for _, f := range Run(target) { if f.Rule == "IOM_280" || f.Rule == "IOM_290" || f.Rule == "IOM_300" || f.Rule == "IOM_310" { t.Fatalf("missing evidence became failure: %#v", f) } }
}

func TestExplicitHostBridgeFailureTriggersIOM310(t *testing.T) {
	target := Target{IOMMUs: []IOMMU{{Name: "iommu0", Enabled: true, DeviceIDBits: 16, PhysAddrBits: 48, MSI: true, ResetMode: "Off", PMPEnforced: true}}, HostBridge: &HostBridgeEvidence{PASID20Provided: boolPtr(false)}}
	found := false
	for _, f := range Run(target) { if f.Rule == "IOM_310" && f.Severity == Critical { found = true } }
	if !found { t.Fatalf("expected critical IOM_310 finding") }
}
