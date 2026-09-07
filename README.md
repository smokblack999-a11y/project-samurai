# StockScan Profit ULTRA

**Business outcome:** purchase document -> validated items -> confirmed inventory -> cost -> selling price -> margin -> expected profit.

This is intentionally not positioned as generic OCR. The product is designed to answer a small retailer's money question: **what did this purchase do to my stock cost and expected profit?**

## Real MVP
1. Photograph/upload a receipt or invoice.
2. OpenAI vision extracts only visible facts into strict structured JSON.
3. Server validates arithmetic and confidence.
4. User confirms before inventory changes.
5. Inventory keeps a purchase ledger with idempotent confirmation.
6. Owner can set a selling price and see margin and expected profit.

## Security and correctness
- `OPENAI_API_KEY` is backend-only. Never put it in the Android APK.
- AI never mutates inventory automatically; confirmation is required.
- Money is persisted as integer minor units.
- Idempotency keys prevent accidental duplicate purchase confirmations.
- Receipt arithmetic and low-confidence extraction produce visible warnings.
- Missing values are not invented by the extraction prompt.

## Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

### API
- `GET /health` — health check
- `POST /v1/receipts/extract` — receipt/invoice extraction + validation
- `POST /v1/inventory/confirm` — confirmation-gated purchase write
- `GET /v1/inventory` — current stock
- `GET /v1/inventory/ledger` — purchase history
- `PUT /v1/inventory/{id}/sale-price` — set selling price
- `GET /v1/dashboard` — stock cost, margin and expected profit

## Commercial wedge
The fastest validation path is a small store/kiosk/cafe pilot. Do not sell "OCR". Sell the workflow: **one photo replaces manual entry and immediately shows the financial effect of the purchase.**

## Android
Android packaging is delegated to GitHub Actions so the app does not depend on a 32-bit Termux/AAPT2 environment. Buildozer produces the APK artifact in CI.
