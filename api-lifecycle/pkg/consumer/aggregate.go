package consumer

import (
 "sort"
 "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

type Summary struct {
 Total int `json:"total"`
 Active int `json:"active"`
 Known int `json:"known"`
 Unknown int `json:"unknown"`
 Requests int64 `json:"requests"`
 Migrated int `json:"migrated"`
}

// Summarize converts raw observations into deterministic consumer evidence.
func Summarize(observations []lifecycle.ConsumerObservation) Summary {
 s := Summary{}
 seen := map[string]bool{}
 ids := make([]string, 0, len(observations))
 for _, o := range observations {
  key := o.ConsumerID
  if key == "" { key = "unknown" }
  if !seen[key] { seen[key] = true; ids = append(ids, key) }
  s.Requests += o.Requests
  if o.Known { s.Known++ } else { s.Unknown++ }
  if o.Migrated { s.Migrated++ }
 }
 sort.Strings(ids)
 s.Total = len(ids)
 s.Active = s.Total - s.Migrated
 return s
}
