package report

import (
	"fmt"
	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/model"
)

func Print(r model.LifecycleRecord, d model.RiskDecision) {
	fmt.Printf("%s %s\n", r.Method, r.Endpoint)
	fmt.Printf("status=%s decision=%s score=%d\n", r.Status, d.Decision, d.Score)
	if len(d.Reasons) > 0 { fmt.Printf("reasons=%v\n", d.Reasons) }
}
