package consumer

import (
    "bufio"
    "encoding/json"
    "fmt"
    "io"
    "time"
)

// JSONLRecord is intentionally small so gateways can export a stable contract
// without coupling SAMURAI to nginx, Envoy, or a specific log format.
type JSONLRecord struct {
    Timestamp string `json:"timestamp"`
    Method string `json:"method"`
    Path string `json:"path"`
    Consumer string `json:"consumer"`
    Status int `json:"status"`
    Bytes int64 `json:"bytes"`
}

func ReadJSONL(r io.Reader) ([]AccessRecord, error) {
    scanner := bufio.NewScanner(r)
    scanner.Buffer(make([]byte, 64*1024), 4*1024*1024)
    var out []AccessRecord
    line := 0
    for scanner.Scan() {
        line++
        var raw JSONLRecord
        if err := json.Unmarshal(scanner.Bytes(), &raw); err != nil {
            return nil, fmt.Errorf("jsonl line %d: %w", line, err)
        }
        ts, err := time.Parse(time.RFC3339, raw.Timestamp)
        if err != nil { return nil, fmt.Errorf("jsonl line %d: invalid timestamp: %w", line, err) }
        out = append(out, AccessRecord{Timestamp: ts, Method: raw.Method, Path: raw.Path, Consumer: raw.Consumer, Status: raw.Status, Bytes: raw.Bytes})
    }
    if err := scanner.Err(); err != nil { return nil, err }
    return out, nil
}
