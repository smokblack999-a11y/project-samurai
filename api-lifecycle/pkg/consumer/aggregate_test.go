package consumer

import (
 "testing"
 "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

func TestSummarizeDeduplicatesConsumers(t *testing.T) {
 got := Summarize([]lifecycle.ConsumerObservation{
  {ConsumerID:"a", Known:true, Requests:10, Migrated:false},
  {ConsumerID:"a", Known:true, Requests:5, Migrated:true},
  {ConsumerID:"b", Known:false, Requests:2},
 })
 if got.Total != 2 || got.Known != 1 || got.Unknown != 1 || got.Requests != 17 || got.Migrated != 1 {
  t.Fatalf("unexpected summary: %+v", got)
 }
}
