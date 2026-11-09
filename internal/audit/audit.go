package audit

import "fmt"

type Severity string

const (
	Critical Severity = "critical"
	High     Severity = "high"
	Medium   Severity = "medium"
	Low      Severity = "low"
)

type NormativeLevel string

const (
	Must   NormativeLevel = "MUST"
	Should NormativeLevel = "SHOULD"
	May    NormativeLevel = "MAY"
)

type Target struct {
	SpecVersion     string             `json:"spec_version"`
	EvidenceSource  string             `json:"evidence_source,omitempty"`
	CPUPhysAddrBits int                `json:"cpu_phys_addr_bits"`
	CPUVModes       []string           `json:"cpu_vm_modes,omitempty"`
	IOMMUs          []IOMMU            `json:"iommus"`
	Devices         []Device           `json:"devices"`
	PCIeRootPorts   []PCIeRootPort    `json:"pcie_root_ports"`
	HostBridge      *HostBridgeEvidence `json:"host_bridge,omitempty"`
}

type IOMMU struct {
	Name            string   `json:"name"`
	Enabled         bool     `json:"enabled"`
	SpecSupported   *bool    `json:"spec_supported,omitempty"`
	VModes          []string `json:"vm_modes,omitempty"`
	DeviceIDBits    int      `json:"device_id_bits"`
	PhysAddrBits    int      `json:"phys_addr_bits"`
	ATS             bool     `json:"ats"`
	T2GPA           bool     `json:"t2gpa"`
	MSI             bool     `json:"msi"`
	ResetMode       string   `json:"reset_mode"`
	PMPEnforced     bool     `json:"pmp_enforced"`
	PCIeHierarchies int      `json:"pcie_hierarchies"`
	PASIDSupported  bool     `json:"pasid_supported"`
	PASIDBits       int      `json:"pasid_bits"`
}

type Device struct {
	Name       string `json:"name"`
	DMACapable bool   `json:"dma_capable"`
	IOMMU      string `json:"iommu"`
	DeviceID   int    `json:"device_id"`
	ATS        bool   `json:"ats"`
	RCiEP      bool   `json:"rciep"`
	PCIe       bool   `json:"pcie"`
	Trusted    bool   `json:"trusted"`
	PASIDBits  int    `json:"pasid_bits"`
	Execute    bool   `json:"execute"`
	Privilege  string `json:"privilege"`
}

type PCIeRootPort struct {
	Name       string `json:"name"`
	IOMMU      string `json:"iommu"`
	ATS        bool   `json:"ats"`
	Accessible bool   `json:"accessible"`
}

// HostBridgeEvidence is intentionally tri-state: nil means the evidence is not
// available yet, while false is an explicit failing observation. This prevents
// the MVP from turning missing evidence into a false compliance failure.
type HostBridgeEvidence struct {
	PCIeRIDProvided      *bool `json:"pcie_rid_provided,omitempty"`
	SegmentProvided      *bool `json:"segment_provided,omitempty"`
	NonPCIeIDsDisjoint   *bool `json:"non_pcie_ids_disjoint,omitempty"`
	PASID20Provided      *bool `json:"pasid20_provided,omitempty"`
	PASIDExecuteProvided *bool `json:"pasid_execute_provided,omitempty"`
	PASIDPrivilegeProvided *bool `json:"pasid_privilege_provided,omitempty"`
}

type Finding struct {
	Rule           string         `json:"rule"`
	Severity       Severity       `json:"severity"`
	NormativeLevel NormativeLevel `json:"normative_level"`
	Confidence     string         `json:"confidence"`
	Status         string         `json:"status"`
	Title          string         `json:"title"`
	Spec           string         `json:"spec"`
	Requirement    string         `json:"requirement"`
	Evidence       string         `json:"evidence"`
	EvidenceSource string         `json:"evidence_source,omitempty"`
	Remediation    string         `json:"remediation"`
}

const specName = "RISC-V Server SoC Requirements v1.0"

func Run(t Target) []Finding {
	var out []Finding
	iom := map[string]IOMMU{}
	for _, x := range t.IOMMUs {
		iom[x.Name] = x
	}

	add := func(rule string, sev Severity, level NormativeLevel, confidence, title, evidence, remediation string) {
		out = append(out, Finding{
			Rule: rule, Severity: sev, NormativeLevel: level, Confidence: confidence,
			Status: "FAIL", Title: title, Spec: specName, Requirement: rule,
			Evidence: evidence, EvidenceSource: t.EvidenceSource, Remediation: remediation,
		})
	}

	// IOM_010: only fail when the input explicitly proves non-support.
	for _, x := range t.IOMMUs {
		if x.SpecSupported != nil && !*x.SpecSupported {
			add("IOM_010", Critical, Must, "high", "IOMMU does not support the declared RISC-V IOMMU specification",
				x.Name, "Implement the applicable ratified RISC-V IOMMU architecture requirements.")
		}
	}

	// IOM_020: every accessible DMA-capable peripheral and PCIe root port must be governed.
	for _, d := range t.Devices {
		if !d.DMACapable {
			continue
		}
		x, ok := iom[d.IOMMU]
		if !ok || !x.Enabled {
			add("IOM_020", Critical, Must, "high", "DMA-capable device is not governed by an active IOMMU",
				fmt.Sprintf("device=%s iommu=%s", d.Name, d.IOMMU),
				"Place the DMA-capable device under an applicable active IOMMU.")
			continue
		}

		// IOM_040 applies only when this IOMMU does not govern a PCIe root port.
		governsRootPort := false
		for _, rp := range t.PCIeRootPorts {
			if rp.IOMMU == x.Name && rp.Accessible {
				governsRootPort = true
				break
			}
		}
		if !governsRootPort && d.DeviceID >= (1<<x.DeviceIDBits) {
			add("IOM_040", High, Must, "high", "Device ID exceeds the modeled IOMMU Device ID width",
				fmt.Sprintf("device=%s device_id=%d bits=%d", d.Name, d.DeviceID, x.DeviceIDBits),
				"Increase Device ID width or correct requester-ID mapping.")
		}

		if d.RCiEP && d.ATS && !x.ATS {
			add("IOM_110", High, Must, "high", "RCiEP ATS capability is not supported by its governing IOMMU",
				d.Name, "Provide ATS support in the governing IOMMU.")
		}
	}

	// IOM_050: when both sides expose their VM modes, every CPU mode must be
	// present in the IOMMU. Missing evidence is not treated as a violation.
	cpuModes := make(map[string]bool, len(t.CPUVModes))
	for _, m := range t.CPUVModes { cpuModes[m] = true }
	for _, x := range t.IOMMUs {
		if len(t.CPUVModes) > 0 && len(x.VModes) > 0 {
			set := make(map[string]bool, len(x.VModes))
			for _, m := range x.VModes { set[m] = true }
			for m := range cpuModes {
				if !set[m] {
					add("IOM_050", High, Must, "high", "IOMMU is missing a page-based virtual-memory mode supported by the CPU harts",
						fmt.Sprintf("iommu=%s missing_mode=%s", x.Name, m),
						"Implement the missing page-based virtual-memory mode/extension in the IOMMU.")
				}
			}
		}
	}

	// Root-port-specific requirements.
	for _, rp := range t.PCIeRootPorts {
		if !rp.Accessible { continue }
		x, ok := iom[rp.IOMMU]
		if !ok || !x.Enabled {
			add("IOM_020", Critical, Must, "high", "Accessible PCIe root port is not governed by an active IOMMU",
				fmt.Sprintf("root_port=%s iommu=%s", rp.Name, rp.IOMMU),
				"Place the PCIe root port under an applicable active IOMMU.")
			continue
		}
		if x.DeviceIDBits < 16 {
			add("IOM_030", High, Must, "high", "PCIe root-port IOMMU has insufficient Device ID width",
				fmt.Sprintf("root_port=%s iommu=%s bits=%d", rp.Name, x.Name, x.DeviceIDBits),
				"Provide at least 16-bit Device IDs for the root-port-governing IOMMU.")
		}
		if rp.ATS && !x.ATS {
			add("IOM_090", Low, Should, "medium", "PCIe root-port integration lacks recommended ATS support",
				rp.Name, "Enable ATS support where the platform threat model and device set require it.")
		}
		if rp.ATS && !x.T2GPA {
			add("IOM_100", Low, Should, "medium", "PCIe root-port ATS lacks recommended T2GPA protection",
				rp.Name, "Enable T2GPA or establish an equivalent authenticated/trusted device path.")
		}
	}

	for _, x := range t.IOMMUs {
		if x.PhysAddrBits < t.CPUPhysAddrBits {
			add("IOM_230", Critical, Must, "high", "IOMMU physical address width is below CPU physical address width",
				fmt.Sprintf("iommu=%s iommu_bits=%d cpu_bits=%d", x.Name, x.PhysAddrBits, t.CPUPhysAddrBits),
				"Increase IOMMU physical address width to cover the CPU physical address space.")
		}
		if x.ResetMode != "Off" {
			add("IOM_240", High, Must, "high", "IOMMU reset mode is not Off",
				fmt.Sprintf("iommu=%s reset_mode=%s", x.Name, x.ResetMode),
				"Reset the IOMMU to the required Off state.")
		}
		if !x.PMPEnforced {
			add("IOM_260", Critical, Must, "high", "IOMMU-originated memory accesses lack modeled PMA/PMP enforcement",
				x.Name, "Enforce PMA/PMP checks on IOMMU-originated memory accesses and signal violations.")
		}
		if !x.MSI {
			add("IOM_130", High, Must, "high", "IOMMU lacks modeled MSI support",
				x.Name, "Implement MSI support for IOMMU external interrupts.")
		}
		if x.PCIeHierarchies > 1 && x.DeviceIDBits < 24 {
			add("IOM_270", High, Must, "high", "IOMMU governing multiple PCIe hierarchies has insufficient Device ID width",
				fmt.Sprintf("iommu=%s hierarchies=%d bits=%d", x.Name, x.PCIeHierarchies, x.DeviceIDBits),
				"Provide 24-bit Device IDs when governing multiple PCIe root ports in different hierarchies.")
		}
		if x.PASIDSupported && x.PASIDBits != 20 {
			add("IOM_170", High, Must, "high", "IOMMU PASID support is not modeled at the required 20-bit width",
				fmt.Sprintf("iommu=%s pasid_bits=%d", x.Name, x.PASIDBits),
				"Support the required 20-bit PASID width when PASID capability is implemented.")
		}
	}

	// IOM_280/290/300/310 are evidence-gated integration rules. They are not
	// inferred from hand-authored device IDs because doing so would create false
	// assurance. Real DTS/register/RTL adapters will populate these fields.
	if t.HostBridge != nil {
		if t.HostBridge.PCIeRIDProvided != nil && !*t.HostBridge.PCIeRIDProvided {
			add("IOM_280", Critical, Must, "high", "Host bridge does not provide PCIe RID in device_id bits 15:0",
				"host_bridge.pcie_rid_provided=false", "Preserve the PCIe RID in device_id bits 15:0.")
		}
		if t.HostBridge.SegmentProvided != nil && !*t.HostBridge.SegmentProvided {
			add("IOM_290", High, Must, "high", "Host bridge does not provide the PCIe segment in device_id bits 23:16",
				"host_bridge.segment_provided=false", "Provide the hierarchy segment number in device_id bits 23:16 when 24-bit IDs are supported.")
		}
		if t.HostBridge.NonPCIeIDsDisjoint != nil && !*t.HostBridge.NonPCIeIDsDisjoint {
			add("IOM_300", Critical, Must, "high", "Non-PCIe device IDs overlap PCIe-derived device IDs",
				"host_bridge.non_pcie_ids_disjoint=false", "Allocate non-overlapping device IDs for PCIe and non-PCIe initiators sharing an IOMMU.")
		}
		if t.HostBridge.PASID20Provided != nil && !*t.HostBridge.PASID20Provided {
			add("IOM_310", Critical, Must, "high", "Host bridge does not provide the full 20-bit PASID to the IOMMU",
				"host_bridge.pasid20_provided=false", "Forward the full 20-bit PASID and its validity indication.")
		}
		if t.HostBridge.PASIDExecuteProvided != nil && !*t.HostBridge.PASIDExecuteProvided {
			add("IOM_310", High, Must, "high", "Host bridge does not provide PASID Execute Requested input",
				"host_bridge.pasid_execute_provided=false", "Forward Execute Requested from the PASID TLP Prefix, or drive it to 0 when PASID is invalid.")
		}
		if t.HostBridge.PASIDPrivilegeProvided != nil && !*t.HostBridge.PASIDPrivilegeProvided {
			add("IOM_310", High, Must, "high", "Host bridge does not provide PASID Privilege Mode Requested input",
				"host_bridge.pasid_privilege_provided=false", "Forward Privilege Mode Requested from the PASID TLP Prefix, or drive it to 0 when PASID is invalid.")
		}
	}

	return out
}

func rank(s Severity) int {
	switch s {
	case Critical: return 4
	case High: return 3
	case Medium: return 2
	case Low: return 1
	default: return 0
	}
}

func ShouldFail(fs []Finding, threshold string) bool {
	if threshold == "none" { return false }
	t := rank(Severity(threshold))
	for _, f := range fs {
		if rank(f.Severity) >= t { return true }
	}
	return false
}
