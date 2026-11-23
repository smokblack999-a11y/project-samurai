# Pre-pilot security checklist

- [ ] OPENAI_API_KEY exists only in runtime environment
- [ ] TDLib credentials are outside Git
- [ ] raw message text is excluded from normal logs
- [ ] duplicate event protection is enabled
- [ ] request body size is bounded
- [ ] evaluation data is de-identified
- [ ] outbound Telegram automation remains disabled by default
