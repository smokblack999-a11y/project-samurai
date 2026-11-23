# Samurai Delivery CRM Bot (MVP)

Isolated Telegram workflow for manual-payment delivery orders. This module does not replace the existing root app or HAMYLION transport.

## Flow
1. Customer starts `/order`, enters order details, phone and delivery address.
2. Bot shows the operator-configured price and payment instructions.
3. Customer submits a Telegram photo receipt; order enters `payment_review`.
4. Admin reviews the receipt and runs `/approve ORDER_ID`.
5. Admin assigns an approved order with `/assign ORDER_ID COURIER_TELEGRAM_ID`.
6. Assigned courier sends a delivery photo; bot marks delivered and forwards the photo to the customer.

## Configuration
Set `TELEGRAM_BOT_TOKEN`, `DELIVERY_ADMIN_IDS` (comma-separated numeric Telegram IDs),
`DELIVERY_PRICE_TEXT`, `DELIVERY_PAYMENT_INSTRUCTIONS`, and optionally
`DELIVERY_DB_PATH`. Never commit real tokens, payment details, or customer data.

Run:
```bash
python -m pip install -r delivery_crm/requirements.txt
python -m delivery_crm.bot
```

The bot uses long polling. Keep it running as a managed process; do not expose the bot token in logs.
The payment step is manual only. No card charging, bank verification, or automated payment confirmation is implemented.
