# ADR-005: Mandate a Governed Semantic Layer and OPA-Enforced MCP Gateway for BI and AI Agents

- **Status**: Accepted
- **Date**: 2026-11-23

## Context
Running multiple BI tools (e.g., Power BI, Apache Superset, Tableau) and conversational AI agents directly against raw Gold tables leads to conflicting KPI calculations ("metric drift"), SQL hallucinations, and unmonitored PII exposure.

## Decision
1. Introduce a **Governed Semantic Layer (`Cube` / `dbt MetricFlow`)** as the mandatory metrics interface for all BI dashboards, Open Data APIs, and AI Agents.
2. Route all AI agent interactions with enterprise APIs, semantic metrics, vector stores, and platform control planes through a **Governed MCP & A2A Gateway** protected by **SPIFFE/SPIRE + OAuth2/OIDC** identities and **OPA Policy-as-Code**.

## Alternatives Considered
| Option | Assessment |
| :--- | :--- |
| Agents generate SQL directly on Gold tables, with guardrails | Flexible. Metric logic is re-derived on every question, and results differ between tools and runs. |
| Metric layers inside each BI tool | No new component. Definitions diverge between tools and are not reachable by agents. |
| Agents call enterprise APIs directly | Simple. No common place for tool policy, audit or approval. |
| API gateway policies only | Reuses an existing control point. Lacks tool-level context such as autonomy level and data classification. |
| **Semantic layer + policy-enforced MCP gateway** | **Chosen.** |

## Consequences
- **Positive**: One KPI definition serves executive dashboards and conversational copilots; verifiable citations; an audited policy decision for every agent tool call.
- **Negative**: The semantic layer becomes a critical dependency and can slow down new metrics. Questions outside the modelled metrics need a governed fallback. The gateway is only as strong as its inputs: identity and delegation are defined in [ADR-007](ADR-007-agent-identity-and-delegated-authority.md), and the rule that risk facts come from the registry and catalog is in [ADR-009](ADR-009-autonomy-levels-and-self-x-safety.md).
