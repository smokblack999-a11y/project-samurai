package telegram

// TDJSON transport boundary.
// The real implementation is intentionally kept behind this interface so the
// application can be tested without Telegram credentials or a live network.
type Transport interface {
    Execute(query []byte) ([]byte, error)
    Send(query []byte) error
    Receive() ([]byte, error)
    Close() error
}

type Adapter struct { transport Transport }
func NewAdapter(t Transport) *Adapter { return &Adapter{transport: t} }
func (a *Adapter) Execute(q []byte) ([]byte, error) { return a.transport.Execute(q) }
