package telegram

import (
	"testing"
)

func TestAdapterExecuteUsesTransport(t *testing.T) {
	fake := &fakeTransport{}
	adapter := NewAdapter(fake)

	got, err := adapter.Execute([]byte(`{"@type":"getAuthorizationState"}`))
	if err != nil {
		t.Fatalf("execute failed: %v", err)
	}
	if string(got) != `{"@type":"ok"}` {
		t.Fatalf("unexpected response: %s", got)
	}
	if len(fake.executed) != 1 {
		t.Fatalf("expected one execute call, got %d", len(fake.executed))
	}
}
