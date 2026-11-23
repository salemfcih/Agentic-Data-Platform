# ADR-002: Combine Apache Polaris (Iceberg REST) with Apache Gravitino (Federated Metalake)

- **Status**: Accepted
- **Date**: 2026-11-23

## Context
Apache Polaris provides a clean, ASF Top-Level Iceberg REST catalog with two-level RBAC and short-lived storage credential vending. However, enterprise estates govern far more than Iceberg tables—they also manage Kafka topics, legacy Hive tables, unstructured AI filesets, and ML model artifacts—and must prevent policy drift between Polaris and Apache Ranger.

## Decision
Retain **Apache Polaris** as the dedicated Iceberg REST Catalog and credential vendor, and deploy **Apache Gravitino** above it as the unified **Federated Metalake** spanning Iceberg, Kafka, unstructured filesets, and AI models, with authorization pushdown into **Apache Ranger**.

## Consequences
- **Positive**: Single unified namespace across data and AI assets; eliminates Ranger vs. Polaris split-brain authorization.
- **Negative**: Adds one lightweight metadata federation service to the control plane, justified by multi-engine governance consistency.
