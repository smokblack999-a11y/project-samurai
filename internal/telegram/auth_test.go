package telegram

import "testing"

func TestAuthMachine(t *testing.T) {
	m := NewAuthMachine()
	if m.Ready() {
		t.Fatal("new auth machine must not be ready")
	}
	m.Apply(AuthWaitPhone)
	if m.State != AuthWaitPhone {
		t.Fatalf("unexpected state: %s", m.State)
	}
	m.Apply(AuthReady)
	if !m.Ready() {
		t.Fatal("ready state not recognized")
	}
}
