from __future__ import annotations

def sales_gate(qualified: int, demos: int, pilots: int, paid: int) -> dict:
    return {
        'qualification_rate': demos / qualified if qualified else 0.0,
        'demo_to_pilot_rate': pilots / demos if demos else 0.0,
        'pilot_to_paid_rate': paid / pilots if pilots else 0.0,
        'first_paid_pass': paid >= 1,
        'scale_pass': paid >= 3,
        'kill_or_reposition': qualified >= 10 and paid == 0,
    }
