package report

import (
    "html/template"
    "io"
)

type HTMLReport struct { Evidence Evidence }

var page = template.Must(template.New("audit").Parse(`<!doctype html><html><head><meta charset="utf-8"><title>API Lifecycle Audit</title><style>body{font:16px system-ui;max-width:900px;margin:40px auto;padding:0 16px} .decision{font-size:28px;font-weight:700} table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:8px;text-align:left}</style></head><body><h1>API Lifecycle Audit</h1><div class="decision">Decision: {{.Evidence.Decision}}</div><p>Endpoint: <b>{{.Evidence.Method}} {{.Evidence.Endpoint}}</b></p><table><tr><th>Metric</th><th>Value</th></tr><tr><td>Consumers</td><td>{{.Evidence.ConsumerCount}}</td></tr><tr><td>Active consumers</td><td>{{.Evidence.ActiveConsumerCount}}</td></tr><tr><td>Unknown traffic</td><td>{{printf "%.2f%%" (mul .Evidence.UnknownTrafficShare 100)}}</td></tr><tr><td>Migration completion</td><td>{{printf "%.2f%%" (mul .Evidence.MigrationCompletion 100)}}</td></tr><tr><td>Replacement healthy</td><td>{{.Evidence.ReplacementHealthy}}</td></tr></table><h2>Reasons</h2><ul>{{range .Evidence.Reasons}}<li>{{.}}</li>{{else}}<li>No blocking reasons.</li>{{end}}</ul></body></html>`)).Funcs(template.FuncMap{"mul": func(a,b float64) float64{return a*b}})

func RenderHTML(w io.Writer, e Evidence) error { return page.Execute(w, HTMLReport{Evidence:e}) }
