# ADR-006: Decouple Ingestion with Kafka + Debezium CDC + dlt; Restrict n8n to Action Triggers

- **Status**: Accepted
- **Date**: 2026-11-23

## Context
Using workflow automation (`n8n`) for analytical API/SaaS ingestion and connecting ingestion directly to `Apache Flink` without an immutable commit log introduces memory bottlenecks, weak schema-contract enforcement, and fragile replay semantics.

## Decision
1. Mandate **Apache Kafka + Schema Registry** as the decoupled event backbone between all streaming producers/CDC connectors and `Apache Flink`.
2. Standardize OLTP ingestion on **Debezium / Kafka Connect (zero-code CDC)**, B2B/SFTP on **Informatica IDMC / NiFi**, and SaaS/REST analytical ELT on **dlt (data load tool) / Airbyte**.
3. Restrict `n8n` strictly to lightweight operational notifications and low-volume human workflow triggers.

## Alternatives Considered
| Option | Assessment |
| :--- | :--- |
| Workflow automation for all ingestion | Fast to start. Lacks schema contracts, change-data checkpoints and bulk throughput. |
| Kafka-compatible or alternative brokers (Redpanda, Pulsar) | Viable backbones. Kafka chosen for ecosystem breadth and connector availability. |
| Direct topic-to-Iceberg sinks without a stream processor | Good for simple append-only topics and worth using there. Not sufficient for joins, enrichment and stateful features. |
| Batch-only ELT | Simplest to operate. Cannot meet near-real-time freshness or serve event-driven automation. |
| **Kafka + Schema Registry, Debezium CDC, dlt for APIs** | **Chosen.** |

## Consequences
- **Positive**: Replay from the log within its retention period, schema compatibility enforced at produce time, and horizontal scaling by partition.
- **Negative**: Kafka, Connect and Schema Registry are a significant platform to operate. Batch API loads and file transfers stay outside the log and need their own contracts and lineage.
