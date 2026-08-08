package lifecycle

import "testing"

func TestValidateRejectsConsumerOverflow(t *testing.T) {
	e := Endpoint{Endpoint: "/v1/orders", Method: "GET", Status: StatusDeprecated, ConsumerCount: 1, ActiveConsumerCount: 2}
	if err := e.Validate(); err == nil {
		t.Fatal("expected consumer validation error")
	}
}

func TestValidateRejectsSunsetWithoutTimestamp(t *testing.T) {
	e := Endpoint{Endpoint: "/v1/orders", Method: "GET", Status: StatusSunset}
	if err := e.Validate(); err == nil {
		t.Fatal("expected sunset timestamp error")
	}
}
