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
	SpecVersion      string          `json:"spec_version"`
	CPUPhysAddrBits  int             `json:"cpu_phys_addr_bits"`
	IOMMUs           []IOMMU         `json:"iommus"`
	Devices          []Device        `json:"devices"`
	PCIeRootPorts    []PCIeRootPort `json:"pcie_root_ports"`
}

type IOMMU struct {
	Name             string `json:"name"`
	Enabled          bool   `json:"enabled"`
	DeviceIDBits     int    `json:"device_id_bits"`
	PhysAddrBits     int    `json:"phys_addr_bits"`
	ATS              bool   `json:"ats"`
	T2GPA            bool   `json:"t2gpa"`
	MSI              bool   `json:"msi"`
	ResetMode        string `json:"reset_mode"`
	PMPEnforced      bool   `json:"pmp_enforced"`
	PCIeHierarchies  int    `json:"pcie_hierarchies"`
	PASIDSupported   bool   `json:"pasid_supported"`
	PASIDBits        int    `json:"pasid_bits"`
}

type Device struct {
	Name        string `json:"name"`
	DMACapable  bool   `json:"dma_capable"`
	IOMMU       string `json:"iommu"`
	DeviceID    int    `json:"device_id"`
	ATS         bool   `json:"ats"`
	RCiEP       bool   `json:"rciep"`
	Trusted     bool   `json:"trusted"`
	PASIDBits   int    `json:"pasid_bits"`
	Execute     bool   `json:"execute"`
	Privilege   string `json:"privilege"`
}

type PCIeRootPort struct {
	Name        string `json:"name"`
	IOMMU       string `json:"iommu"`
	ATS         bool   `json:"ats"`
	Accessible  bool   `json:"accessible"`
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
	Remediation    string         `json:"remediation"`
}

const specName = "RISC-V Server SoC Requirements 1.0"

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
			Evidence: evidence, Remediation: remediation,
		})
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

		// IOM_110 is a MUST for RCiEPs; ATS support itself is a SHOULD for root ports.
		if d.RCiEP && d.ATS && !x.ATS {
			add("IOM_110", High, Must, "high", "RCiEP ATS capability is not supported by its governing IOMMU",
				d.Name, "Provide ATS support in the governing IOMMU.")
		}
	}

	// Root-port-specific requirements.
	for _, rp := range t.PCIeRootPorts {
		if !rp.Accessible {
			continue
		}
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

	return out
}

func rank(s Severity) int {
	switch s {
	case Critical:
		return 4
	case High:
		return 3
	case Medium:
		return 2
	case Low:
		return 1
	default:
		return 0
	}
}

func ShouldFail(fs []Finding, threshold string) bool {
	if threshold == "none" {
		return false
	}
	t := rank(Severity(threshold))
	for _, f := range fs {
		if rank(f.Severity) >= t {
			return true
		}
	}
	return false
}
