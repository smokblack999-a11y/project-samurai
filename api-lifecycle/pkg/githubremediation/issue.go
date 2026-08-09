package githubremediation

import (
    "fmt"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
)

type IssueAction struct {
    Title string `json:"title"`
    Body string `json:"body"`
    Fingerprint string `json:"fingerprint"`
    Close bool `json:"close"`
}

func BuildIssueAction(e report.Evidence) (IssueAction, error) {
    p, err := Build(e)
    if err != nil { return IssueAction{}, err }
    if e.Decision == "SAFE" {
        return IssueAction{Title: p.Title, Body: fmt.Sprintf("Re-audit is now SAFE. Evidence fingerprint: `%s`.\n\nThe previous remediation can be resolved.", p.Fingerprint), Fingerprint: p.Fingerprint, Close: true}, nil
    }
    return IssueAction{Title: p.Title, Body: p.Body, Fingerprint: p.Fingerprint, Close: false}, nil
}
