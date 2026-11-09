# Pilot Data Policy

Store only the fields needed to evaluate lead qualification: stable event id, redacted message text, model decision, human label and business outcome.

Do not store phone numbers, usernames, access tokens, API keys or raw Telegram exports in the repository. Keep credentials server-side in environment/secret storage. Do not enable autonomous outbound messaging during the pilot.
