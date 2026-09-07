package audit

import "fmt"

type Severity string
const (
    Critical Severity = "critical"
    High Severity = "high"
    Medium Severity = "medium"
    Low Severity = "low"
)

type Target struct {
    SpecVersion string `json:"spec_version"`
    CPUPhysAddrBits int `json:"cpu_phys_addr_bits"`
    IOMMUs []IOMMU `json:"iommus"`
    Devices []Device `json:"devices"`
    PCIeRootPorts []PCIeRootPort `json:"pcie_root_ports"`
}
type IOMMU struct {
    Name string `json:"name"`
    Enabled bool `json:"enabled"`
    DeviceIDBits int `json:"device_id_bits"`
    PhysAddrBits int `json:"phys_addr_bits"`
    ATS bool `json:"ats"`
    T2GPA bool `json:"t2gpa"`
    MSI bool `json:"msi"`
    ResetMode string `json:"reset_mode"`
    PMPEnforced bool `json:"pmp_enforced"`
    PCIeHierarchies int `json:"pcie_hierarchies"`
}
type Device struct {
    Name string `json:"name"`
    DMACapable bool `json:"dma_capable"`
    IOMMU string `json:"iommu"`
    DeviceID int `json:"device_id"`
    ATS bool `json:"ats"`
    RCiEP bool `json:"rciep"`
    Trusted bool `json:"trusted"`
    PASIDBits int `json:"pasid_bits"`
    Execute bool `json:"execute"`
    Privilege string `json:"privilege"`
}
type PCIeRootPort struct { Name string `json:"name"`; IOMMU string `json:"iommu"`; ATS bool `json:"ats"` }

type Finding struct {
    Rule string `json:"rule"`; Severity Severity `json:"severity"`; Status string `json:"status"`; Title string `json:"title"`
    Spec string `json:"spec"`; Requirement string `json:"requirement"`; Evidence string `json:"evidence"`; Remediation string `json:"remediation"`
}

func Run(t Target) []Finding {
    var out []Finding
    iom := map[string]IOMMU{}
    for _, x := range t.IOMMUs { iom[x.Name] = x }
    add := func(rule string, sev Severity, req, title, evidence, remediation string) { out = append(out, Finding{rule,sev,"FAIL",title,"RISC-V Server SoC Requirements 1.0",req,evidence,remediation}) }

    for _, d := range t.Devices {
        if !d.DMACapable { continue }
        x, ok := iom[d.IOMMU]
        if !ok || !x.Enabled { add("IOM_020", Critical,"IOM_020","DMA-capable device is not governed by an active IOMMU",fmt.Sprintf("device=%s iommu=%s",d.Name,d.IOMMU),"Place the DMA-capable device under an applicable IOMMU.") }
        if ok && d.DeviceID >= (1 << x.DeviceIDBits) { add("IOM_040", High,"IOM_040","Device ID exceeds the modeled IOMMU Device ID width",fmt.Sprintf("device_id=%d bits=%d",d.DeviceID,x.DeviceIDBits),"Increase Device ID width or correct requester-ID mapping.") }
        if ok && d.ATS && !x.ATS { add("IOM_090", High,"IOM_090","Device uses ATS but governing IOMMU lacks ATS support",d.Name,"Enable compatible ATS support or disable ATS for the governed device.") }
        if ok && d.RCiEP && d.ATS && !x.ATS { add("IOM_110", High,"IOM_110","RCiEP ATS capability is not supported by its governing IOMMU",d.Name,"Provide ATS support in the governing IOMMU.") }
        if ok && !d.Trusted && d.ATS && !x.T2GPA { add("IOM_100", High,"IOM_100","ATS is enabled without the modeled T2GPA/trust protection",d.Name,"Add T2GPA support or an equivalent authenticated/trusted request path.") }
        if ok && d.PASIDBits > 0 && d.PASIDBits > 20 { add("IOM_160", Medium,"IOM_160","PASID width exceeds the modeled supported width",fmt.Sprintf("device=%s pasid_bits=%d",d.Name,d.PASIDBits),"Align PASID width with the supported IOMMU interface.") }
    }
    for _, x := range t.IOMMUs {
        if x.PhysAddrBits < t.CPUPhysAddrBits { add("IOM_230", Critical,"IOM_230","IOMMU physical address width is below CPU physical address width",fmt.Sprintf("iommu=%s iommu_bits=%d cpu_bits=%d",x.Name,x.PhysAddrBits,t.CPUPhysAddrBits),"Increase IOMMU physical address width to cover the CPU physical address space.") }
        if x.ResetMode != "Off" { add("IOM_240", High,"IOM_240","IOMMU reset mode is not Off",fmt.Sprintf("iommu=%s reset_mode=%s",x.Name,x.ResetMode),"Reset the IOMMU to the required Off state.") }
        if !x.PMPEnforced { add("IOM_260", Critical,"IOM_260","IOMMU-originated memory accesses lack modeled PMA/PMP enforcement",x.Name,"Enforce PMA/PMP checks on IOMMU-originated memory accesses.") }
        if !x.MSI { add("IOM_130", Medium,"IOM_130","IOMMU lacks modeled MSI support",x.Name,"Implement MSI support for IOMMU external interrupts.") }
        if x.PCIeHierarchies > 1 && x.DeviceIDBits < 24 { add("IOM_270", High,"IOM_270","IOMMU governing multiple PCIe hierarchies has insufficient Device ID width",fmt.Sprintf("iommu=%s hierarchies=%d bits=%d",x.Name,x.PCIeHierarchies,x.DeviceIDBits),"Provide at least the required Device ID width for multiple PCIe hierarchies.") }
    }
    return out
}

func rank(s Severity) int { switch s { case Critical:return 4; case High:return 3; case Medium:return 2; case Low:return 1 }; return 0 }
func ShouldFail(fs []Finding, threshold string) bool { if threshold=="none" { return false }; t:=rank(Severity(threshold)); for _,f:=range fs { if rank(f.Severity)>=t{return true} }; return false }
