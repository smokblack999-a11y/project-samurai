package system

import (
	"testing"
	"time"
)

func TestBuildStatusExposesDisabledDependenciesClearly(t *testing.T) {
	s := BuildStatus("test", time.Now(), false, false)
	if !s.OK {
		t.Fatal("system should be structurally healthy")
	}
	if s.Telegram.Enabled || s.AI.Enabled {
		t.Fatal("disabled components must report disabled")
	}
	if !s.Database.Ready {
		t.Fatal("sqlite should be ready for the MVP")
	}
}
