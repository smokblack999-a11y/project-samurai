package telegram

type fakeTransport struct {
	executed []string
	sent     []string
	received []string
}

func (f *fakeTransport) Execute(query []byte) ([]byte, error) {
	f.executed = append(f.executed, string(query))
	return []byte(`{"@type":"ok"}`), nil
}

func (f *fakeTransport) Send(query []byte) error {
	f.sent = append(f.sent, string(query))
	return nil
}

func (f *fakeTransport) Receive() ([]byte, error) {
	if len(f.received) == 0 {
		return nil, nil
	}
	value := f.received[0]
	f.received = f.received[1:]
	return []byte(value), nil
}

func (f *fakeTransport) Close() error { return nil }
