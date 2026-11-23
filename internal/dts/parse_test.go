package dts

import "testing"

const sample = `/dts-v1/;
/iommu0 {
    compatible = "riscv,iommu";
    interrupts = <0x20>;
};

pcie@1000 {
    compatible = "pci-host-ecam-generic";
    iommus = <&iommu0 0x2a>;
};`

func TestParseExtractsIOMMUDMAAndInterruptEvidence(t *testing.T) {
	e, err := Parse("board.dts", sample)
	if err != nil { t.Fatal(err) }
	if e.Source != "board.dts" || e.IOMMUCount != 1 || e.DMADevices != 1 || e.Interrupts != 1 { t.Fatalf("unexpected evidence: %#v", e) }
}

func TestParseUintCell(t *testing.T) {
	got, err := ParseUintCell("0x2a")
	if err != nil || got != 42 { t.Fatalf("got=%d err=%v", got, err) }
	got, err = ParseUintCell("17")
	if err != nil || got != 17 { t.Fatalf("got=%d err=%v", got, err) }
}

func TestParseRejectsEmpty(t *testing.T) {
	if _, err := Parse("x.dts", " "); err == nil { t.Fatal("expected error") }
}
