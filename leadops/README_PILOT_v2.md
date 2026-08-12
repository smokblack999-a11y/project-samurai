# Execute the pilot

1. Copy `labeling_template.jsonl` to a private local file.
2. Add only consented, redacted messages.
3. Validate with `python label_dataset.py private/messages.jsonl`.
4. Run `python evaluation.py`.
5. Configure the existing server-side `OPENAI_API_KEY` locally; never commit it.
6. Run `python benchmark.py`.
7. Review false positives and false negatives.
8. Calculate ROI only from observed business outcomes.
9. Run the 7-day pilot with human approval for outbound actions.
10. Record payment outcome before adding new product scope.
