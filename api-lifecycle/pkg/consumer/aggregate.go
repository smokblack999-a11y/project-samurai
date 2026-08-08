package consumer

import (
	"sort"
	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

type Summary struct {
	Total int `json:"total"`
	Known int `json:"known"`
	Unknown int `json:"unknown"`
	Requests int64 `json:"requests"`
	Migrated int `json:"migrated"`
}

func Summarize(observations []lifecycle.ConsumerObservation) Summary {
	s := Summary{}
	seen := map[string]bool{}
	for _, o := range observations {
		key := o.ConsumerID
		if key == "" { key = "unknown" }
		if !seen[key] { seen[key] = true; s.Total++; if o.Known { s.Known++ } else { s.Unknown++ } }
		s.Requests += o.Requests
		if o.Migrated { s.Migrated++ }
	}
	return s
}

// StableConsumerIDs returns unique IDs in deterministic order for reports and tests.
func StableConsumerIDs(observations []lifecycle.ConsumerObservation) []string {
	set := map[string]struct{}{}
	for _, o := range observations { id := o.ConsumerID; if id == "" { id = "unknown" }; set[id] = struct{}{} }
	ids := make([]string, 0, len(set))
	for id := range set { ids = append(ids, id) }
	sort.Strings(ids)
	return ids
}
