package telegram

import "errors"

type Update struct { Type string; Data []byte }

type Client interface {
    Send(query []byte) error
    Receive() ([]byte, error)
    Close() error
}

var ErrNotConfigured = errors.New("tdjson is not configured")

type TDJSONClient struct{}

func NewTDJSONClient() *TDJSONClient { return &TDJSONClient{} }
func (c *TDJSONClient) Send(_ []byte) error { return ErrNotConfigured }
func (c *TDJSONClient) Receive() ([]byte, error) { return nil, ErrNotConfigured }
func (c *TDJSONClient) Close() error { return nil }
