package risk

// Policy defines hard safety gates. Keep this separate from scoring so a
// future AI/heuristic layer cannot silently weaken shutdown safety.
type Policy struct {
    MaxUnknownTrafficShare float64 `json:"max_unknown_traffic_share"`
    RequireReplacement      bool    `json:"require_replacement"`
    RequireHealthyReplacement bool  `json:"require_healthy_replacement"`
}

var DefaultPolicy = Policy{
    MaxUnknownTrafficShare: 0.01,
    RequireReplacement: true,
    RequireHealthyReplacement: true,
}
