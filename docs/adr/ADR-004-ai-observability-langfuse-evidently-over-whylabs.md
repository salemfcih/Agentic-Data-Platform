# ADR-004: Replace WhyLabs with Evidently AI (ML Drift) + Langfuse (GenAI & Agent Observability)

- **Status**: Accepted
- **Date**: 2026-11-23

## Context
`WhyLabs, Inc.` discontinued commercial operations in 2026, leaving `whylogs` without vendor SLA or active enterprise maintenance. Furthermore, agentic AI systems require deep trace-level observability (prompts, RAG citations, tool calls, latency, token spend, and LLM-as-a-judge evaluations) beyond statistical tabular profiling.

## Decision
Replace WhyLabs with a dual open-source observability layer:
- **Evidently AI** for classical tabular data quality, covariate drift, and ML model performance monitoring.
- **Langfuse** (self-hostable on OpenShift) for LLM/agent trace capture, prompt versioning correlation, RAG faithfulness scoring, and cost telemetry, bridged via OpenTelemetry to Grafana LGTM.

## Consequences
- **Positive**: Active open-source communities, full sovereign self-hosting, and direct telemetry feeds into the Self-Improve autonomous control loop.
