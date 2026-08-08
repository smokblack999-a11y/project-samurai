package lifecycle

import "strings"

func EndpointKey(method, path string) string { return strings.ToUpper(strings.TrimSpace(method)) + " " + strings.TrimSpace(path) }
