# Evaluation dataset schema

JSONL fields:

- `id`: stable case ID
- `text`: source message
- `intent`: buying | information
- `human_score`: 0..100
- `human_action`: human_followup | auto_reply
- `notes`: optional reviewer rationale

Production gate: do not treat synthetic labels as customer evidence. Real pilot samples must be anonymized and labeled by a human reviewer.