# Human-led agent workflow

This repository contains **specialist rule-based processing stages** (also called agents here), rather than a claim that autonomous LLM workers are deployed.

1. **Source Agent**: read an allowlisted public API, with fixed endpoints and bounded queries.
2. **Analysis Agent**: normalize results, detect matches, and calculate transparent relevance signals.
3. **Verification Agent**: check source IDs, links, missing fields, timestamps and provenance.
4. **Report Agent**: produce JSON with source links, warnings and limitations.
5. **Human reviewer**: decides whether evidence supports the final conclusion or further action.

Implementation roles for future contributors: Research → Architecture → Builder → QA → Security → Documentation. Every change requires tests and human review before production.

Security: no private keys in Git, no unapproved writes or emails, no secret-bearing logs, no unverified claims of eligibility or truth, no automated high-impact action. On upstream failure, raise an error instead of substituting invented records.

A future LLM orchestrator would require deliberate prompts, task boundaries, bounded tools, evaluations, auditing, and user approval before any irreversible actions. FastMCP is the tool transport, not the reasoning agent.
