package io

import (
	"encoding/json"
	"fmt"
	"os"
	"github.com/smokblack999-a11y/project-samurai/api-lifecycle/internal/model"
)

func LoadRecords(path string) ([]model.LifecycleRecord, error) {
	b, err := os.ReadFile(path)
	if err != nil { return nil, fmt.Errorf("read %s: %w", path, err) }
	var records []model.LifecycleRecord
	if err := json.Unmarshal(b, &records); err != nil {
		var single model.LifecycleRecord
		if err2 := json.Unmarshal(b, &single); err2 != nil { return nil, fmt.Errorf("parse %s: %w", path, err) }
		records = []model.LifecycleRecord{single}
	}
	return records, nil
}
