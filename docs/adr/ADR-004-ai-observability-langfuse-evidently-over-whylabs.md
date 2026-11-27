# ADR-004: Replace WhyLabs with Evidently AI (ML Drift) + Langfuse (GenAI & Agent Observability)

- **Status**: Accepted
- **Date**: 2026-11-23

## Context
`WhyLabs, Inc.` discontinued commercial operations in early 2025 and open-sourced its platform, leaving `whylogs` without vendor SLA or active enterprise maintenance. Furthermore, agentic AI systems require deep trace-level observability (prompts, RAG citations, tool calls, latency, token spend, and LLM-as-a-judge evaluations) beyond statistical tabular profiling.

## Decision
Replace WhyLabs with a dual open-source observability layer:
- **Evidently AI** for classical tabular data quality, covariate drift, and ML model performance monitoring.
- **Langfuse** (self-hostable on OpenShift) for LLM/agent trace capture, prompt versioning correlation, RAG faithfulness scoring, and cost telemetry, bridged via OpenTelemetry to Grafana LGTM.

## Alternatives Considered
| Option | Assessment |
| :--- | :--- |
| Self-host the open-sourced WhyLabs platform | Possible, but the adopter would maintain a codebase whose vendor has stopped operating. |
| Arize Phoenix | Capable open-source LLM tracing and evaluation. A reasonable substitute for Langfuse; choose one. |
| MLflow tracing and evaluation only | Fewer components. Less depth for agent traces and production drift monitoring at the time of writing. |
| Enterprise APM only | Good for infrastructure. Does not score faithfulness, drift or tool-call accuracy. |
| **Evidently AI + Langfuse** | **Chosen.** |

## Consequences
- **Positive**: Active open-source communities, full sovereign self-hosting, and direct telemetry feeds into the Self-Improve autonomous control loop.
- **Negative**: Two more services to run. Prompts and completions are personal-data carriers, so traces need redaction at collection and short retention ([ADR-010](ADR-010-resilience-tenancy-and-data-lifecycle.md)).
