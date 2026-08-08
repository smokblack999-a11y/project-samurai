package parser

import (
 "encoding/json"
 "fmt"
 "os"
 "github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/model"
)

func LoadRecords(path string) ([]model.LifecycleRecord, error) {
 b, err := os.ReadFile(path)
 if err != nil { return nil, err }
 var records []model.LifecycleRecord
 if err := json.Unmarshal(b, &records); err != nil { return nil, fmt.Errorf("parse lifecycle JSON: %w", err) }
 for i, r := range records {
  if r.Endpoint == "" || r.Method == "" { return nil, fmt.Errorf("record %d: endpoint and method are required", i) }
  if r.TrafficShare < 0 || r.TrafficShare > 1 || r.UnknownTrafficShare < 0 || r.UnknownTrafficShare > 1 || r.MigrationCompletion < 0 || r.MigrationCompletion > 1 { return nil, fmt.Errorf("record %d: ratio out of range", i) }
 }
 return records, nil
}
