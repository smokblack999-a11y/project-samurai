package main

import (
    "encoding/json"
    "flag"
    "fmt"
    "os"

    "github.com/smokblack999-a11y/project-samurai/api-lifecycle/pkg/inventory"
)

func main() {
    input := flag.String("openapi", "", "OpenAPI/Swagger JSON file")
    flag.Parse()
    if *input == "" { fmt.Fprintln(os.Stderr, "usage: samurai-inventory -openapi api.json"); os.Exit(2) }

    f, err := os.Open(*input)
    if err != nil { fatal(err) }
    defer f.Close()

    endpoints, err := inventory.Read(f)
    if err != nil { fatal(err) }
    out, err := json.MarshalIndent(endpoints, "", "  ")
    if err != nil { fatal(err) }
    fmt.Println(string(out))
}

func fatal(err error) { fmt.Fprintln(os.Stderr, "inventory error:", err); os.Exit(1) }
