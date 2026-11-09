# AgentCheck V2 benchmark

The benchmark measures signal quality, not exploitability.

## Initial targets

- `NousResearch/hermes-agent`
- `browser-use/browser-use`
- `crewAIInc/crewAI`
- `HKUDS/nanobot`

These were selected because they represent different agent architectures and have public source code. The benchmark must record evidence before assigning a finding.

## Current external evidence

A direct source inspection of `browser-use/browser-use/browser_use/skills/install.py` shows legitimate use of `subprocess.run()` for installing a tool. This is an explicit false-positive guard for `TOOL-001`: generic installer/build subprocess usage must not automatically become an agent unrestricted-execution finding.

Source: https://github.com/browser-use/browser-use/blob/main/browser_use/skills/install.py

## Protocol

1. Pin the repository ref used for each run.
2. Run AgentCheck in static mode.
3. Store rule ID, file, line, evidence, severity and confidence.
4. Manually classify each finding as true-positive, false-positive or uncertain.
5. Do not call a static signal a vulnerability.
6. Add every confirmed false-positive as a regression fixture.
7. Only promote a rule when its evidence is reproducible.

## Commercial gate

The benchmark is successful only if it produces findings that are:

- reproducible;
- understandable to an engineering buyer;
- actionable;
- cheaper/faster to obtain than a manual review;
- defensible without claiming more certainty than the evidence supports.

The next product step is a paid Agent Production Readiness Review, not an immediate SaaS launch.
