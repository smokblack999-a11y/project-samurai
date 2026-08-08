package consumer

import "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"

type Summary struct {
 Total int `json:"total"`
 Known int `json:"known"`
 Unknown int `json:"unknown"`
 Requests int64 `json:"requests"`
 Migrated int `json:"migrated"`
}

// Summarize converts observations into deterministic consumer evidence.
// It deliberately does not infer "active" from migration state: activity
// requires a time-window policy and LastSeen data, which belongs in a later layer.
func Summarize(observations []lifecycle.ConsumerObservation) Summary {
 s := Summary{}
 seen := map[string]bool{}
 for _, o := range observations {
  key := o.ConsumerID
  if key == "" { key = "unknown" }
  if !seen[key] {
   seen[key] = true
   s.Total++
   if o.Known { s.Known++ } else { s.Unknown++ }
  }
  s.Requests += o.Requests
  if o.Migrated { s.Migrated++ }
 }
 return s
}
