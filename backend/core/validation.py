from .schemas import Receipt, ValidationResult

def validate_receipt(receipt: Receipt) -> ValidationResult:
    warnings = []
    calculated = sum(item.line_total for item in receipt.items)
    tolerance = max(2.0, receipt.total * 0.03)
    if abs(calculated - receipt.total) > tolerance:
        warnings.append(f"line totals {calculated:.2f} differ from total {receipt.total:.2f}")
    low = [item.name for item in receipt.items if item.confidence < 0.70]
    if low:
        warnings.append("low confidence: " + ", ".join(low[:10]))
    if receipt.total == 0:
        warnings.append("zero total")
    return ValidationResult(valid=not warnings, warnings=warnings)
