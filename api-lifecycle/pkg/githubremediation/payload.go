package githubremediation

import (
    "crypto/sha256"
    "encoding/hex"
    "fmt"
    "sort"
    "strings"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/report"
    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/remediation"
)

type Payload struct {
    Title string `json:"title"`
    Body string `json:"body"`
    Fingerprint string `json:"fingerprint"`
    Decision string `json:"decision"`
}

func Build(e report.Evidence) (Payload, error) {
    b, err := remediation.Build(e)
    if err != nil { return Payload{}, err }
    fp := fingerprint(e)
    title := fmt.Sprintf("API retirement %s: %s %s", e.Decision, e.Method, e.Endpoint)
    var sb strings.Builder
    fmt.Fprintf(&sb, "## API Retirement Safety Audit\n\n**Decision:** `%s`  \n**Score:** `%d`  \n**Confidence:** `%d%%`  \n**Evidence fingerprint:** `%s`\n\n", e.Decision, e.Score, e.Confidence, fp)
    if len(e.AffectedConsumers) > 0 { sb.WriteString("### Affected consumers\n"); for _, c := range e.AffectedConsumers { fmt.Fprintf(&sb, "- `%s`\n", c) }; sb.WriteString("\n") }
    if len(e.Reasons) > 0 { sb.WriteString("### Blockers / reasons\n"); for _, r := range e.Reasons { fmt.Fprintf(&sb, "- %s\n", r) }; sb.WriteString("\n") }
    if len(b.Actions) > 0 { sb.WriteString("### Ordered remediation\n"); for i, a := range b.Actions { fmt.Fprintf(&sb, "%d. **%s** — %s\n", i+1, a.Action, a.Why) }; sb.WriteString("\n") }
    sb.WriteString("> This issue is evidence-driven. No automatic destructive API shutdown is performed. Re-run the audit after remediation.")
    return Payload{Title:title, Body:sb.String(), Fingerprint:fp, Decision:e.Decision}, nil
}

func fingerprint(e report.Evidence) string {
    consumers := append([]string(nil), e.AffectedConsumers...); sort.Strings(consumers)
    reasons := append([]string(nil), e.Reasons...); sort.Strings(reasons)
    raw := strings.Join([]string{e.Method, e.Endpoint, e.Decision, fmt.Sprint(e.Score), fmt.Sprint(e.Confidence), strings.Join(consumers, "|"), strings.Join(reasons, "|")}, "\x00")
    sum := sha256.Sum256([]byte(raw))
    return hex.EncodeToString(sum[:])
}
