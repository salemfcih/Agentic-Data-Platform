# ADR-005: Mandate a Governed Semantic Layer and OPA-Enforced MCP Gateway for BI and AI Agents

- **Status**: Accepted
- **Date**: 2026-11-23

## Context
Running multiple BI tools (e.g., Power BI, Apache Superset, Tableau) and conversational AI agents directly against raw Gold tables leads to conflicting KPI calculations ("metric drift"), SQL hallucinations, and unmonitored PII exposure.

## Decision
1. Introduce a **Governed Semantic Layer (`Cube` / `dbt MetricFlow`)** as the mandatory metrics interface for all BI dashboards, Open Data APIs, and AI Agents.
2. Route 100% of AI agent interactions with enterprise APIs, semantic metrics, vector stores, and platform control planes through a **Governed MCP & A2A Gateway** protected by **SPIFFE/SPIRE + OAuth2/OIDC** identities and **OPA Policy-as-Code**.

## Consequences
- **Positive**: Identical KPI numbers across executive dashboards and conversational copilots; verifiable citations; auditable Zero-Trust guardrails for every autonomous agent action.
