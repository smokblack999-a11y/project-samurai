package consumer

import (
    "bufio"
    "encoding/json"
    "io"
    "strings"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

type AccessRecord struct {
    Method string `json:"method"`
    Path string `json:"path"`
    Consumer string `json:"consumer"`
    Requests int64 `json:"requests"`
}

type Attribution struct {
    ConsumerCount int `json:"consumer_count"`
    ActiveConsumerCount int `json:"active_consumer_count"`
    UnknownTrafficShare float64 `json:"unknown_traffic_share"`
}

func ReadJSONL(r io.Reader) ([]AccessRecord, error) {
    s := bufio.NewScanner(r)
    out := make([]AccessRecord, 0)
    for s.Scan() {
        line := strings.TrimSpace(s.Text())
        if line == "" { continue }
        var v AccessRecord
        if err := json.Unmarshal([]byte(line), &v); err != nil { return nil, err }
        if v.Requests <= 0 { v.Requests = 1 }
        out = append(out, v)
    }
    return out, s.Err()
}

func Attribute(endpoint lifecycle.Endpoint, records []AccessRecord) Attribution {
    consumers := map[string]bool{}
    var total, unknown int64
    for _, r := range records {
        if r.Method != "" && !strings.EqualFold(r.Method, endpoint.Method) { continue }
        if r.Path != "" && r.Path != endpoint.Endpoint { continue }
        n := r.Requests
        total += n
        if strings.TrimSpace(r.Consumer) == "" { unknown += n; continue }
        consumers[r.Consumer] = true
    }
    share := float64(0)
    if total > 0 { share = float64(unknown) / float64(total) }
    return Attribution{ConsumerCount:len(consumers), ActiveConsumerCount:len(consumers), UnknownTrafficShare:share}
}
