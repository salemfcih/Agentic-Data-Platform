# ADR-002: Combine Apache Polaris (Iceberg REST) with Apache Gravitino (Federated Metalake)

- **Status**: Accepted
- **Date**: 2026-11-23

## Context
Apache Polaris provides a clean, ASF Top-Level Iceberg REST catalog with two-level RBAC and short-lived storage credential vending. However, enterprise estates govern far more than Iceberg tables—they also manage Kafka topics, legacy Hive tables, unstructured AI filesets, and ML model artifacts—and must prevent policy drift between Polaris and Apache Ranger.

## Decision
Retain **Apache Polaris** as the dedicated Iceberg REST Catalog and credential vendor, and deploy **Apache Gravitino** above it as the unified **Federated Metalake** spanning Iceberg, Kafka, unstructured filesets, and AI models, with authorization pushdown into **Apache Ranger**.

## Alternatives Considered
| Option | Assessment |
| :--- | :--- |
| Polaris only | Simplest. Leaves Kafka topics, filesets and models without a common namespace or governance. |
| Gravitino only, using its own Iceberg REST service | One component fewer. Viable, and worth re-evaluating. Not chosen here so that the Iceberg REST catalog stays independent of the federation layer. |
| Unity Catalog (open source) | Covers tables and AI assets. Its ecosystem centres on a different table format and engine set than this reference. |
| Project Nessie | Strong Git-like catalog semantics for tables. Does not address non-tabular assets. |
| **Polaris + Gravitino** | **Chosen.** |

## Consequences
- **Positive**: Single unified namespace across data and AI assets. It gives a place from which to reduce policy drift between Ranger and Polaris, but that does not happen by itself: [ADR-008](ADR-008-authorization-enforcement-matrix.md) defines the single policy source, the enforcement matrix and the drift check needed to achieve it.
- **Negative**: Adds one metadata federation service to the control plane, and a third place where grants can exist next to Polaris and Ranger.
