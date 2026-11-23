# ADR-006: Decouple Ingestion with Kafka + Debezium CDC + dlt; Restrict n8n to Action Triggers

- **Status**: Accepted
- **Date**: 2026-11-23

## Context
Using workflow automation (`n8n`) for analytical API/SaaS ingestion and connecting ingestion directly to `Apache Flink` without an immutable commit log introduces memory bottlenecks, weak schema-contract enforcement, and fragile replay semantics.

## Decision
1. Mandate **Apache Kafka + Schema Registry** as the decoupled event backbone between all streaming producers/CDC connectors and `Apache Flink`.
2. Standardize OLTP ingestion on **Debezium / Kafka Connect (zero-code CDC)**, B2B/SFTP on **Informatica IDMC / NiFi**, and SaaS/REST analytical ELT on **dlt (data load tool) / Airbyte**.
3. Restrict `n8n` strictly to lightweight operational notifications and low-volume human workflow triggers.

## Consequences
- **Positive**: Guaranteed replayability, strict Avro/JSON schema contract enforcement, and linear horizontal scaling under peak loads.
