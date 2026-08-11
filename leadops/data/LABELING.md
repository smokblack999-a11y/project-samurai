# Human labeling contract

Use one row per inbound message. Remove names, phone numbers, addresses, payment data and other unnecessary personal data before import.

Intent: `buying | information | support | spam_other`.

Urgency: `low | high`.

Action: `human_followup | auto_reply | ignore`.

Lead score is human judgment from 0 to 100. Do not infer purchase intent from politeness alone. Mark uncertainty in `notes`.

Commercial benchmark requires at least 100 real, consented/authorized messages from one pilot source before making a sales-quality claim.
