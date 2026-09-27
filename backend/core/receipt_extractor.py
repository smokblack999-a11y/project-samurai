import json
from .config import get_settings
from .openai_client import get_client
from .image import image_to_data_url
from .retry import retry_openai
from .schemas import Receipt

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "merchant": {"type": ["string", "null"]},
        "currency": {"type": "string"},
        "receipt_date": {"type": ["string", "null"]},
        "items": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "properties": {
                "name": {"type": "string"}, "sku": {"type": ["string", "null"]},
                "quantity": {"type": "number"}, "unit_price": {"type": "number"},
                "line_total": {"type": "number"}, "confidence": {"type": "number"}
            },
            "required": ["name", "sku", "quantity", "unit_price", "line_total", "confidence"]
        }},
        "subtotal": {"type": ["number", "null"]}, "tax": {"type": ["number", "null"]},
        "total": {"type": "number"}, "confidence": {"type": "number"}
    },
    "required": ["merchant", "currency", "receipt_date", "items", "subtotal", "tax", "total", "confidence"]
}

@retry_openai()
def extract(raw: bytes) -> Receipt:
    settings = get_settings()
    response = get_client().responses.create(
        model=settings.openai_model,
        instructions=("Extract only facts visible in the receipt/invoice. Never invent missing values. "
                       "Never treat the grand total as an item. Use confidence from 0 to 1."),
        input=[{"role": "user", "content": [
            {"type": "input_text", "text": "Extract this purchase document."},
            {"type": "input_image", "image_url": image_to_data_url(raw), "detail": "high"}
        ]}],
        text={"format": {"type": "json_schema", "name": "receipt", "strict": True, "schema": SCHEMA}}
    )
    return Receipt.model_validate(json.loads(response.output_text))
