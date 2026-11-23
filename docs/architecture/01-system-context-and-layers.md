# 01 — System Context, Core Layers & Merged Capabilities

## Architectural Vision
AegisLake converges two historically fragmented enterprise planes—**Real-Time Integration (API, Event Streaming, B2B/MFT, ODS)** and **Analytical Lakehouse & AI (Medallion Zones, Feature Store, MLOps, GenAI & Autonomous Agents)**—into a single contract-governed, data-product-centric platform.

## Architectural Principles
1. **Data Products as the Default Unit of Delivery**: Every reusable Dataset, Dashboard/KPI bundle, and AI Model is published as a certified Data Product with a named owner, ODCS contract, quality SLA, lineage, and lifecycle policy.
2. **Event-First, Replayable Ingestion**: All state changes flow through a durable, schema-governed commit log (`Kafka + Schema Registry`) before hitting stateful stream processors (`Flink`) or lakehouse tables (`Iceberg`).
3. **Open Formats, Zero Lock-In**: Table storage (`Apache Iceberg v3`), catalog protocol (`Iceberg REST / Polaris`), federated metadata (`Apache Gravitino`), and observability (`OpenTelemetry + OpenLineage`) remain strictly open standards.
4. **Semantic Grounding Before AI Generation**: Both BI dashboards and conversational AI agents query governed KPI definitions from the **Semantic Layer** (`Cube / dbt MetricFlow`), eliminating metric drift and SQL hallucination.
5. **Zero-Trust Identity for Humans AND Agents**: Autonomous agents authenticate via cryptographic workload identities (`SPIFFE/SPIRE` + `OAuth2/OIDC`) and execute exclusively through a policy-enforced **MCP & A2A Gateway**.

---

## Layer-by-Layer Responsibilities

### Layer 0 — Data Sources & Ecosystem
- Internal operational databases (Oracle, PostgreSQL, ERP, CRM, core domain systems)
- Microservices publishing canonical domain events
- External partner & regulatory APIs, SaaS applications, webhooks
- B2B/SFTP batch partner feeds and unstructured document/media corpora (PDFs, forms, audio, images)

### Layer 1 — Unified Integration, Ingestion & Operational Data Store (ODS)
- **API Gateway (`Apigee Hybrid / Kong`)**: External/internal API lifecycle, mTLS, OAuth2/OIDC, throttling, developer portal, and controlled exposure of APIs as MCP tools.
- **Event Backbone (`Confluent Kafka / Strimzi + Schema Registry`)**: Immutable event log enforcing Avro/JSON Schema compatibility and AsyncAPI event catalogs.
- **Zero-Code CDC (`Debezium / Kafka Connect`)**: Low-latency transactional replication from OLTP databases and partner SFTP/HTTP sources with zero custom code.
- **Modern ELT (`dlt / Airbyte`)**: Schema-evolving batch ingestion for REST APIs and SaaS platforms.
- **B2B / MFT & Edge Routing (`Informatica IDMC / Apache NiFi`)**: Governed managed file transfer, partner onboarding, and edge provenance routing.
- **Operational Data Store (ODS) & MDM Golden Records**: Low-latency operational serving and mastered golden-record entity resolution feeding both real-time apps and the Silver Lakehouse zone.

### Layer 2 — Open Multimodal Lakehouse & Federated Metalake
- **Sovereign Object Storage (`Apache Ozone / Ceph RGW / Cloud S3`)**: Durable, S3-compatible storage tier replacing archived MinIO Community Edition.
- **Structured Table Layer (`Apache Iceberg v3`)**: Medallion zones (**Bronze** immutable raw, **Silver** cleansed/conformed/Data Vault 2.0, **Gold** dimensional domain marts) with ACID guarantees, hidden partitioning, time travel, and **Write-Audit-Publish (WAP)** branching.
- **Unstructured Versioning (`LakeFS`)**: Git-like branching/tagging scoped strictly to unstructured AI corpora (documents, audio, video, model checkpoints) to avoid conflict with Iceberg table refs.
- **Hybrid Knowledge Store (`Qdrant / LanceDB + Neo4j`)**: Vector embeddings and entity knowledge graphs for hybrid RAG retrieval.
- **Catalog & Federated Metalake (`Apache Polaris + Apache Gravitino`)**: Polaris serves as the standard Iceberg REST catalog with short-lived credential vending; Gravitino federates governance across Iceberg, Kafka topics, unstructured filesets, and ML models.

### Layer 3 — Elastic Compute, Data Products & Semantic Serving
- **Stream Processing (`Apache Flink`)**: Stateful event-time windowing, CDC enrichment, real-time alerts, and streaming feature computation managed via the Flink Kubernetes Operator.
- **Batch & Distributed AI Compute (`Apache Spark + Ray`)**: Large-scale ETL, Iceberg table maintenance/compaction, and distributed multimodal AI preprocessing.
- **Modular Transformations (`SQLMesh / dbt Core`)**: Version-controlled SQL transformations with virtual data environments, unit tests, and automated lineage emission.
- **Query Serving & Data Virtualization (`Trino + StarRocks`)**: Trino handles federated analytical SQL and zero-copy virtualization across heterogeneous stores; StarRocks serves high-concurrency, sub-second operational OLAP.
- **Governed Semantic Layer & KPI Library (`Cube / dbt MetricFlow`)**: Single source of truth for certified enterprise metrics consumed by Power BI, Apache Superset, Open Data portals, and AI Agents.
- **Dual Orchestration (`Airflow 3.x + Temporal`)**: Airflow 3.x manages asset-aware data DAGs; Temporal guarantees durable, stateful execution for long-running agentic workflows and compensating transactions.

### Layer 4 — Unified ML, GenAI & 7-Sub-Capability Agentic Plane
Integrating transformational MLOps (CI/CT/CD) with the **7 GenAI & Agentic Architectural Sub-Capabilities**:
1. **Knowledge Build Pipelines**: Source connectors, Document AI / OCR parsing & semantic chunking, multilingual embeddings generation, metadata + ACL security tagging, incremental index refresh.
2. **Knowledge Layer**: Document/chunk object store, Vector DB/index (`Qdrant`), structured Gold-zone knowledge base, and metadata store.
3. **Retrieval Layer**: Hybrid retriever service (BM25 + vector + graph), cross-encoder reranking, context window builder, and verifiable citations package.
4. **Orchestration & Prompting**: Versioned prompt templates (`MLflow`), deterministic/dynamic workflow routing, structured tool/function calling, and session state management.
5. **Agent Runtime & Tooling**: Short- and long-term agent memory store, governed tool registry, **MCP Server / MCP Gateway**, sandboxed tool execution runtime, and multi-agent (**A2A**) coordination (`LangGraph` on OpenShift).
6. **Foundation Model Access**: Enterprise LLM Gateway (`LiteLLM / Envoy AI Gateway`) providing sovereign on-prem + cloud model routing, automatic fallback, token rate limits, cost controls, and secrets management.
7. **Serving, Guardrails & Observability**: Unified inference (`KServe` running `vLLM` for LLMs + `Triton/ONNX` for classical ML), input/output safety guardrails (PII, prompt injection, jailbreak), immutable audit logging, `Langfuse` + `Evidently AI` monitoring, and Human-in-the-Loop (HITL) escalation.

### Layer 5 — Experience, Data Products & Consumption
- **BI & Self-Service Analytics**: Power BI, Apache Superset, or Looker backed exclusively by the Semantic Layer.
- **AI Workbench**: JupyterHub/JupyterLab, reactive Marimo notebooks, and containerized OpenShift Dev Spaces with GPU/MIG sharing.
- **Conversational & Digital Channels**: Multilingual Arabic/English conversational BI copilots, domain portals, and embedded predictive insights.
- **Governed Data Exchange**: Automated internal/external data sharing and open-data marketplace replacing manual ticket-based exports.
