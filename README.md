# StockScan Profit ULTRA

Real MVP: photo of receipt/invoice -> OpenAI vision -> strict JSON -> validation -> confirmation -> inventory -> economics.

## Security
- OPENAI_API_KEY is backend-only. Never put it in the Android APK.
- AI never mutates inventory automatically; confirmation is required.
- Money is persisted as integer minor units.

## Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Endpoints: `GET /health`, `POST /v1/receipts/extract`, `POST /v1/inventory/confirm`, `GET /v1/inventory`.

Android packaging is delegated to GitHub Actions so the app does not depend on a 32-bit Termux/AAPT2 environment.
