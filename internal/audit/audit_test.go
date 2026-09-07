package audit

import "testing"

func TestCleanTargetHasNoFindings(t *testing.T) {
	target := Target{
		SpecVersion: "1.0", CPUPhysAddrBits: 48,
		IOMMUs: []IOMMU{{Name: "iommu0", Enabled: true, DeviceIDBits: 16, PhysAddrBits: 48, ATS: true, T2GPA: true, MSI: true, ResetMode: "Off", PMPEnforced: true}},
		Devices: []Device{{Name: "nvme0", DMACapable: true, IOMMU: "iommu0", DeviceID: 42}},
	}
	if got := Run(target); len(got) != 0 {
		t.Fatalf("expected no findings, got %d: %#v", len(got), got)
	}
}

func TestRootPortRulesUse030AndNot040(t *testing.T) {
	target := Target{
		SpecVersion: "1.0", CPUPhysAddrBits: 48,
		IOMMUs: []IOMMU{{Name: "iommu0", Enabled: true, DeviceIDBits: 8, PhysAddrBits: 48, MSI: true, ResetMode: "Off", PMPEnforced: true}},
		PCIeRootPorts: []PCIeRootPort{{Name: "rp0", IOMMU: "iommu0", Accessible: true}},
	}
	findings := Run(target)
	if len(findings) != 1 || findings[0].Rule != "IOM_030" {
		t.Fatalf("expected exactly IOM_030, got %#v", findings)
	}
}

func TestPASIDUsesIOM170(t *testing.T) {
	target := Target{
		SpecVersion: "1.0", CPUPhysAddrBits: 48,
		IOMMUs: []IOMMU{{Name: "iommu0", Enabled: true, DeviceIDBits: 16, PhysAddrBits: 48, MSI: true, ResetMode: "Off", PMPEnforced: true, PASIDSupported: true, PASIDBits: 17}},
	}
	findings := Run(target)
	if len(findings) != 1 || findings[0].Rule != "IOM_170" || findings[0].NormativeLevel != Must {
		t.Fatalf("expected MUST IOM_170 finding, got %#v", findings)
	}
}

func TestShouldRulesDoNotFailHighGate(t *testing.T) {
	findings := []Finding{{Rule: "IOM_090", Severity: Low, NormativeLevel: Should}}
	if ShouldFail(findings, "high") {
		t.Fatal("SHOULD/advisory finding must not trip high security gate")
	}
}

func TestCriticalFindingTripsHighGate(t *testing.T) {
	findings := []Finding{{Rule: "IOM_260", Severity: Critical, NormativeLevel: Must}}
	if !ShouldFail(findings, "high") {
		t.Fatal("critical MUST finding must trip high security gate")
	}
}
