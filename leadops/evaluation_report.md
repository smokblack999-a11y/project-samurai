# LeadOps Evaluation Gate

The evaluation suite is deliberately deterministic and provider-independent. It measures the baseline classifier before OpenAI is enabled.

Required release threshold:

- intent accuracy >= 90%
- recommended-action accuracy >= 90%
- score-threshold rate >= 90%

This is a release gate, not evidence of market fit. A separate commercial gate is required: 10 qualified prospects -> 5 demos -> 3 pilots -> 1 paid pilot.

The next evaluation expansion should contain 50-100 anonymized or synthetic messages representing the first target ICP, including hard negatives and ambiguous intent. Do not claim production accuracy from the current 8-case suite.
