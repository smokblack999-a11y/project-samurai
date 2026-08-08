package risk

import (
 "testing"
 "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

func TestDecideBlocked(t *testing.T) { e:=lifecycle.Endpoint{Replacement:"/v2",ReplacementHealthy:true}; r:=Decide(e, .02); if r.Decision!=lifecycle.DecisionBlocked { t.Fatalf("got %s",r.Decision) } }
func TestDecideReview(t *testing.T) { e:=lifecycle.Endpoint{Replacement:"/v2",ReplacementHealthy:true,ActiveConsumerCount:1,MigrationCompletion:1}; r:=Decide(e, 0); if r.Decision!=lifecycle.DecisionReview { t.Fatalf("got %s",r.Decision) } }
func TestDecideSafe(t *testing.T) { e:=lifecycle.Endpoint{Replacement:"/v2",ReplacementHealthy:true,ActiveConsumerCount:0,MigrationCompletion:1}; r:=Decide(e, 0); if r.Decision!=lifecycle.DecisionSafe { t.Fatalf("got %s",r.Decision) } }
