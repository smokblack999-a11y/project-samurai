package consumer

import (
    "regexp"
    "strings"
    "time"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/lifecycle"
)

// AccessRecord is the normalized representation of one HTTP access-log event.
type AccessRecord struct {
    Timestamp time.Time
    Method    string
    Path      string
    Consumer  string
    Status    int
    Bytes     int64
}

// Attribution summarizes observed traffic for an endpoint. Unknown traffic is
// deliberately preserved rather than guessed: shutdown decisions must fail closed.
type Attribution struct {
    Endpoint            string  `json:"endpoint"`
    Requests            int64   `json:"requests"`
    KnownRequests       int64   `json:"known_requests"`
    UnknownRequests     int64   `json:"unknown_requests"`
    UnknownTrafficShare float64 `json:"unknown_traffic_share"`
    ConsumerCount       int     `json:"consumer_count"`
    ActiveConsumerCount int     `json:"active_consumer_count"`
}

func Attribute(endpoint lifecycle.Endpoint, records []AccessRecord) Attribution {
    a := Attribution{Endpoint: endpoint.Endpoint}
    consumers := map[string]bool{}
    active := map[string]bool{}
    for _, r := range records {
        if !sameEndpoint(endpoint.Endpoint, r.Path) || strings.ToUpper(r.Method) != strings.ToUpper(endpoint.Method) {
            continue
        }
        a.Requests++
        id := strings.TrimSpace(r.Consumer)
        if id == "" {
            a.UnknownRequests++
            continue
        }
        a.KnownRequests++
        consumers[id] = true
        active[id] = true
    }
    a.ConsumerCount = len(consumers)
    a.ActiveConsumerCount = len(active)
    if a.Requests > 0 {
        a.UnknownTrafficShare = float64(a.UnknownRequests) / float64(a.Requests)
    }
    return a
}

var wildcard = regexp.MustCompile(`\{[^/]+\}`)

func sameEndpoint(template, path string) bool {
    template = strings.TrimSuffix(template, "/")
    path = strings.TrimSuffix(path, "/")
    if template == path { return true }
    partsA, partsB := strings.Split(template, "/"), strings.Split(path, "/")
    if len(partsA) != len(partsB) { return false }
    for i := range partsA {
        if wildcard.MatchString(partsA[i]) { continue }
        if partsA[i] != partsB[i] { return false }
    }
    return true
}
