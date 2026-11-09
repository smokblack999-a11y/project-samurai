package dts

import (
	"strings"
	"testing"
)

func TestParseBasicNodes(t *testing.T) {
	input := `/dts-v1/;

/ {
	iommu0: iommu@10000000 {
		compatible = "riscv,iommu";
		status = "okay";
		reg = <0x10000000 0x1000>;
	};

	pcie@20000000 {
		compatible = "pci-host-ecam-generic", "foo";
		status = "disabled";
	};
};`
	nodes, err := Parse(strings.NewReader(input))
	if err != nil { t.Fatal(err) }
	if len(nodes) != 2 { t.Fatalf("expected 2 nodes, got %d", len(nodes)) }
	if nodes[0].Status != "okay" || len(nodes[0].Compatible) != 1 || nodes[0].Properties["reg"] == "" { t.Fatalf("bad iommu evidence: %#v", nodes[0]) }
	if nodes[1].Status != "disabled" || len(nodes[1].Compatible) != 2 { t.Fatalf("bad pcie evidence: %#v", nodes[1]) }
}

func TestU32Hex(t *testing.T) {
	n, err := U32("<0x10000000>")
	if err != nil || n != 0x10000000 { t.Fatalf("unexpected parse: %x %v", n, err) }
}
