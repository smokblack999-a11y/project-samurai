package main

import (
    "encoding/json"
    "os"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
)

func writeBundle(path string, evidence report.Evidence) error {
    bundle, err := report.BuildBundle(evidence)
    if err != nil { return err }
    b, err := json.MarshalIndent(bundle, "", "  ")
    if err != nil { return err }
    return os.WriteFile(path, b, 0644)
}
