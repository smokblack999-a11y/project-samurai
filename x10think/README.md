# X10THINK Sentinel

A local-first infrastructure health agent with guarded AI diagnostics.

## Run

```bash
cd x10think
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export TOGETHER_API_KEY='YOUR_KEY'   # optional
# export OPENAI_API_KEY='YOUR_EXISTING_KEY'  # optional fallback
python doctor.py
python -m uvicorn api:app --host 127.0.0.1 --port 7010
```

Open `http://127.0.0.1:7010/`.

## AI routing

`X10_AI_PROVIDER=auto` uses Together AI when `TOGETHER_API_KEY` is present and falls back to OpenAI if Together fails. Set `X10_AI_PROVIDER=together` or `openai` to force one provider.

Together is integrated through the OpenAI-compatible `chat.completions` interface at `https://api.together.ai/v1`. Together's Responses API is not supported, so this project intentionally uses chat completions for that provider.

Example local environment:

```bash
export TOGETHER_API_KEY='...'
export X10_TOGETHER_MODEL='openai/gpt-oss-20b'
export X10_TOGETHER_REASONING='low'
```

Never commit API keys. GitHub push protection can block supported secrets before they enter a repository.

## API

- `GET /status` — compact status
- `GET /system/status` — unified dashboard status
- `GET /health` — telemetry and findings
- `POST /scan` — health plus optional AI analysis
- `POST /analyze` — analyze supplied telemetry
- `POST /action?name=health` — allow-listed local action

## Safety boundary

The agent never exposes arbitrary shell execution to the AI. Actions are explicitly allow-listed in `core.py`. AI output is treated as untrusted text and is not executed. This is a product requirement, not an implementation detail.

## Production direction

The next monetizable layer is not another generic chatbot. It is a small infrastructure reliability product: continuous health scoring, incident evidence, guarded remediation suggestions, audit history, alerts, and team-level reporting. Keep the local-first agent as the engine and put paid workflow, collaboration, and retention features around it.
