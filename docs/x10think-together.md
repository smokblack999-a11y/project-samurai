# X10THINK + Together AI

Together AI is an optional diagnostics provider. The core agent remains local-first and does not execute model-generated shell commands.

## Configuration

Copy `.env.example` into the runtime environment and set `TOGETHER_API_KEY`. Together project keys are scoped to a project; keep the key outside source control. The provider uses the OpenAI-compatible chat completions endpoint at `https://api.together.ai/v1`.

## Safety contract

- The key is read only from the environment.
- Prompts are bounded by the API layer before forwarding.
- Model output is returned as text and is never executed.
- Authentication, rate-limit, timeout, and malformed-response errors are normalized.
- Use a separate development/CI project key rather than a production key.

## Commercial path

Together lowers the cost barrier for a service-led infrastructure audit. The first monetizable offer should remain an audit/setup/monitoring package, not an unvalidated generic AI subscription.
