package headers

import (
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"time"
)

const (
	Deprecation = "Deprecation"
	Sunset      = "Sunset"
	Link        = "Link"
)

// Apply writes RFC 9745 Deprecation and RFC 8594 Sunset metadata.
// It intentionally does not infer policy: callers must provide the dates.
func Apply(h http.Header, deprecatedAt *time.Time, sunsetAt *time.Time, replacement string) {
	if deprecatedAt != nil {
		h.Set(Deprecation, "@"+strconv.FormatInt(deprecatedAt.Unix(), 10))
	}
	if sunsetAt != nil {
		h.Set(Sunset, sunsetAt.UTC().Format(http.TimeFormat))
	}
	if replacement != "" {
		h.Add(Link, fmt.Sprintf("<%s>; rel=\"successor-version\"", replacement))
	}
}

func ParseDeprecation(value string) (*time.Time, error) {
	value = strings.TrimSpace(value)
	if !strings.HasPrefix(value, "@") {
		return nil, fmt.Errorf("unsupported Deprecation value %q: expected @unix-seconds", value)
	}
	seconds, err := strconv.ParseInt(strings.TrimPrefix(value, "@"), 10, 64)
	if err != nil {
		return nil, fmt.Errorf("invalid Deprecation timestamp: %w", err)
	}
	t := time.Unix(seconds, 0).UTC()
	return &t, nil
}

func ParseSunset(value string) (*time.Time, error) {
	t, err := http.ParseTime(strings.TrimSpace(value))
	if err != nil {
		return nil, fmt.Errorf("invalid Sunset HTTP-date: %w", err)
	}
	return &t, nil
}
