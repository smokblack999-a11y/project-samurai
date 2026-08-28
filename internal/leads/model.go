package leads

import "time"

type Lead struct {
    ID        int64     `json:"id"`
    ChatID    int64     `json:"chat_id"`
    Status    string    `json:"status"`
    Score     int       `json:"score"`
    Source    string    `json:"source"`
    CreatedAt time.Time `json:"created_at"`
}

func ValidStatus(s string) bool {
    switch s { case "new", "qualified", "won", "lost": return true }
    return false
}
