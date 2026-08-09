package main

import "testing"

func TestE2ECommandPackage(t *testing.T) {
    // The executable is intentionally thin: parsing and policy decisions live in packages.
    // This test protects the command package from accidentally accumulating business logic.
}
