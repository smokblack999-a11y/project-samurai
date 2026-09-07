from pydantic import BaseModel, Field, ConfigDict

class ReceiptItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=200)
    sku: str | None = None
    quantity: float = Field(gt=0)
    unit_price: float = Field(ge=0)
    line_total: float = Field(ge=0)
    confidence: float = Field(ge=0, le=1)

class Receipt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    merchant: str | None = None
    currency: str = "KZT"
    receipt_date: str | None = None
    items: list[ReceiptItem] = Field(min_length=1, max_length=500)
    subtotal: float | None = None
    tax: float | None = None
    total: float = Field(ge=0)
    confidence: float = Field(ge=0, le=1)

class ValidationResult(BaseModel):
    valid: bool
    warnings: list[str] = []

class ConfirmItem(BaseModel):
    name: str
    quantity: float = Field(gt=0)
    unit_price_minor: int = Field(ge=0)
    currency: str = "KZT"

class ConfirmRequest(BaseModel):
    items: list[ConfirmItem] = Field(min_length=1)
