package report

import (
 "encoding/json"
 "fmt"
 "os"
 "github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/model"
)

type Item struct { Record model.LifecycleRecord `json:"record"`; Decision model.DecisionResult `json:"decision"` }

func WriteJSON(path string, items []Item) error {
 b, err := json.MarshalIndent(items, "", "  ")
 if err != nil { return fmt.Errorf("encode report: %w", err) }
 return os.WriteFile(path, append(b, '\n'), 0644)
}
