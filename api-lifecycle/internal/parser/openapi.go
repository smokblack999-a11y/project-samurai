package parser

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/model"
)

type openapiDoc struct { Paths map[string]map[string]json.RawMessage `json:"paths"` }

func LoadJSON(path string) ([]model.LifecycleRecord, error) {
	b, err := os.ReadFile(path); if err != nil { return nil, err }
	var doc openapiDoc
	if err := json.Unmarshal(b, &doc); err != nil { return nil, fmt.Errorf("openapi json: %w", err) }
	allowed := map[string]bool{"get":true,"post":true,"put":true,"patch":true,"delete":true,"head":true,"options":true}
	var out []model.LifecycleRecord
	for route, methods := range doc.Paths {
		for method := range methods {
			if !allowed[method] { continue }
			out = append(out, model.LifecycleRecord{Endpoint:route, Method:method, Status:model.StatusActive, MigrationCompletion:1, ReplacementHealthy:true})
		}
	}
	return out, nil
}
