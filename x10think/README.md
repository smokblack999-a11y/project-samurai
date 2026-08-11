# X10THINK Sentinel

A local-first infrastructure health agent with guarded AI diagnostics.

## Run

```bash
cd x10think
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# Together AI (recommended low-cost default)
export TOGETHER_API_KEY='YOUR_KEY'
export X10_AI_PROVIDER=together
export X10_TOGETHER_MODEL='openai/gpt-oss-20b'

# Or OpenAI
# export OPENAI_API_KEY='YOUR_EXISTING_KEY'
# export X10_AI_PROVIDER=openai

python doctor.py
python -m uvicorn api:app --host 127.0.0.1 --port 7010
```

Open `http://127.0.0.1:7010/`.

`X10_AI_PROVIDER=auto` selects Together when `TOGETHER_API_KEY` exists, otherwise OpenAI when `OPENAI_API_KEY` exists. AI is optional; local health checks still work without either key.

## API

- `GET /status` — compact status
- `GET /health` — telemetry and findings
- `POST /scan` — health plus optional AI analysis
- `POST /analyze` — analyze supplied telemetry
- `POST /action?name=health` — allow-listed local action

## AI contract

Together uses the OpenAI-compatible chat-completions endpoint with structured JSON output. Together's Responses API is not used because Together documents `/v1/responses` as unsupported; `chat.completions.create` is the portable path. The default `openai/gpt-oss-20b` model is listed by Together with structured-output support and current serverless pricing of $0.05/M input and $0.20/M output tokens. See the official Together documentation for current model availability and pricing.

The application never stores an API key in the repository. Use environment variables locally. Never paste a real key into Git or source code. GitHub push protection can block supported secrets before they reach a repository.

## Safety boundary

The first release deliberately does not expose arbitrary shell execution to the AI. Actions must be explicitly allow-listed in `core.py`. This is a product requirement, not an implementation detail.
