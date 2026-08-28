# Real pilot dataset

Use only anonymized, consented or otherwise authorized real Telegram messages for the commercial benchmark.

Required fields: `id`, `text`, `intent`, `score`, `action`.

Target: first 100 messages from one real pilot.

Before storage, remove names, phone numbers, emails, usernames, payment data, session files and unrelated personal data. Keep production exports outside Git unless explicitly sanitized and authorized.

The benchmark must record annotator policy and source consent separately from the message text.
