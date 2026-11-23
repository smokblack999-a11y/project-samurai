from .schemas import Receipt, ValidationResult


def validate_receipt(receipt: Receipt) -> ValidationResult:
    warnings = []
    calculated_lines = 0.0

    for item in receipt.items:
        expected = item.quantity * item.unit_price
        line_tolerance = max(0.02, abs(expected) * 0.01)
        if abs(item.line_total - expected) > line_tolerance:
            warnings.append(
                f"item '{item.name}' arithmetic mismatch: {item.line_total:.2f} vs {expected:.2f}"
            )
        calculated_lines += item.line_total

    if receipt.subtotal is not None:
        subtotal_tolerance = max(0.05, abs(receipt.subtotal) * 0.01)
        if abs(calculated_lines - receipt.subtotal) > subtotal_tolerance:
            warnings.append(
                f"line totals {calculated_lines:.2f} differ from subtotal {receipt.subtotal:.2f}"
            )

    expected_total = receipt.subtotal if receipt.subtotal is not None else calculated_lines
    if receipt.tax is not None and receipt.subtotal is not None:
        expected_total = receipt.subtotal + receipt.tax

    total_tolerance = max(0.05, abs(receipt.total) * 0.01)
    if abs(expected_total - receipt.total) > total_tolerance:
        warnings.append(f"calculated total {expected_total:.2f} differs from total {receipt.total:.2f}")

    low = [item.name for item in receipt.items if item.confidence < 0.70]
    if low:
        warnings.append("low confidence: " + ", ".join(low[:10]))
    if receipt.confidence < 0.70:
        warnings.append(f"document confidence is low: {receipt.confidence:.2f}")
    if receipt.total == 0:
        warnings.append("zero total")

    return ValidationResult(valid=not warnings, warnings=warnings)
