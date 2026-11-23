# AegisLake — Self-Evolving Agentic Data & AI Platform

[![License](https://img.shields.io/badge/License-Apache_2.0-1F4E5F.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/Architecture-Open_Lakehouse_%2B_Agentic_AI-007ACC.svg)](docs/architecture/01-system-context-and-layers.md)
[![Governance](https://img.shields.io/badge/Governance-Zero_Trust_%7C_NIST_SP_800--207-2E7D32.svg)](docs/architecture/03-zero-trust-responsible-ai-governance.md)
[![Standards](https://img.shields.io/badge/Contracts-ODCS_v3_%7C_AsyncAPI_3.0_%7C_MCP-6A1B9A.svg)](contracts/)

**AegisLake** is a vendor-neutral, enterprise-grade reference architecture for a **Self-Operating, Self-Healing, Self-Evolving, Self-Improving, Self-Governing, and Self-Scaling Agentic Data & AI Lakehouse**.

Designed for regulated national-scale enterprises (government, financial services, insurance, telecom), AegisLake unifies:
- **Open Multimodal Lakehouse** (`Apache Ozone / Ceph RGW`, `Apache Iceberg v3`, `Apache Polaris`, `Apache Gravitino`, `LakeFS`, `Qdrant`)
- **Event-First Integration & Operational Data Store** (`Confluent Kafka / Strimzi`, `Debezium CDC`, `Informatica IDMC / NiFi`, `dlt`, `Apigee Hybrid`, `ODS + MDM Golden Records`)
- **Elastic Compute, Data Products & Semantic Serving** (`Apache Flink`, `Apache Spark + Ray`, `SQLMesh / dbt`, `Trino + StarRocks`, `Cube / dbt MetricFlow`, `Airflow 3.x + Temporal`)
- **7-Layer GenAI, MLOps & Governed Agentic Runtime** (`Feast`, `MLflow 3.x`, `KServe + vLLM / Triton`, `LangGraph`, `Governed MCP & A2A Gateway`, `Evidently AI`, `Langfuse`)
- **6 Autonomous "Self-X" Control Loops** backed by `OpenTelemetry`, `OpenLineage`, `DataHub`, `Apache Ranger`, `OPA`, and `KEDA` on Red Hat OpenShift / Kubernetes
- **Dual Sovereign On-Premises & Cloud-Native Deployment Mapping** (balancing strict data sovereignty with frontier AI velocity)

---

## Target Reference Architecture

```mermaid
flowchart TB
    subgraph L0["0. DATA SOURCES & ECOSYSTEM"]
        SRC_DB["OLTP & Core Systems (Oracle / Postgres / ERP / CRM)"]
        SRC_EVT["Microservices & Domain Event Producers"]
        SRC_API["External APIs / SaaS / Webhooks"]
        SRC_B2B["Partner B2B / SFTP / Unstructured Documents & Media"]
    end

    subgraph L1["1. UNIFIED INTEGRATION, INGESTION & ODS PLANE"]
        APIGEE["API Gateway (Apigee Hybrid / Kong) + mTLS"]
        KAFKA["Event Backbone (Kafka + Schema Registry + AsyncAPI)"]
        CDC["Zero-Code CDC & Connectors (Debezium / Kafka Connect)"]
        DLT["Modern ELT (dlt / Airbyte)"]
        MFT["B2B / MFT & Edge Routing (IDMC / Apache NiFi)"]
        ODS["Operational Data Store (ODS) & MDM Golden Records"]
    end

    subgraph L2["2. OPEN MULTIMODAL LAKEHOUSE & FEDERATED METALAKE"]
        OBJ["Sovereign Object Storage (Apache Ozone / Ceph RGW / S3)"]
        ICEBERG["Apache Iceberg v3 (Bronze / Silver / Gold + Native WAP)"]
        LAKEFS["LakeFS (Unstructured AI Corpora & Multimodal Versioning)"]
        VEC["Hybrid Knowledge Store (Vector DB: Qdrant + Graph DB: Neo4j)"]
        POLARIS["Apache Polaris (Iceberg REST Catalog + Credential Vending)"]
        GRAV["Apache Gravitino (Federated Metalake: Tables, Topics, Filesets, Models)"]
    end

    subgraph L3["3. COMPUTE, DATA PRODUCTS & SEMANTIC SERVING"]
        FLINK["Apache Flink (Stateful Streaming, CDC & Real-Time Features)"]
        SPARK["Apache Spark + Ray (Batch ETL, Compaction & Distributed AI)"]
        DBT["SQLMesh / dbt Core (Medallion & Data Vault 2.0 Transforms)"]
        TRINO["Trino + StarRocks (Federated SQL, Virtualization & High-QPS OLAP)"]
        SEM["Governed Semantic Layer & KPI Library (Cube / dbt MetricFlow)"]
        ORCH["Airflow 3.x (Data Assets) + Temporal (Durable Agent Workflows)"]
    end

    subgraph L4["4. UNIFIED ML, GENAI & AGENTIC EXECUTION PLANE (7 SUB-CAPABILITIES)"]
        KB["Knowledge Build Pipelines (OCR / Document AI, Chunking, Embeddings, ACL Tagging)"]
        FEAST["Feast (Offline Iceberg + Online Valkey Feature Store)"]
        MLFLOW["MLflow 3.x (Model, Prompt & Eval Registry — CI/CT/CD)"]
        KSERVE["KServe + vLLM / Triton (Sovereign LLMs + Classical ML Serving)"]
        MCP["Governed MCP & A2A Gateway (Tool Registry, LLM Routing, Guardrails, HITL)"]
        AGENTS["Domain & Platform Agents (LangGraph / OpenShift Pods + Memory)"]
    end

    subgraph L5["5. EXPERIENCE, DATA PRODUCTS & CONSUMPTION"]
        BI["Semantic-Backed BI (Power BI / Apache Superset / Looker)"]
        DS["AI Workbench (JupyterLab / Marimo / Dev Spaces)"]
        CONV["Conversational BI, Copilots & Autonomous Workflows"]
        EXCH["Governed Data Exchange / Open Data Marketplace"]
    end

    subgraph CTRL["6. AUTONOMOUS 'SELF-X' CONTROL PLANE"]
        OBS["Unified Observability: OpenTelemetry + Grafana LGTM + OpenLineage"]
        AIOBS["Quality & AI Eval: Soda v4 (ODCS) + Evidently AI + Langfuse"]
        OPSA["Self-Operate (AIOps / FinOps Agent: Compaction, Clustering, Tiering)"]
        HEALA["Self-Heal (Data Reliability Agent: WAP Quarantine, Schema Fix, DLQ Replay)"]
        EVOLVA["Self-Evolve (Architecture Agent: AsyncAPI -> dbt/Semantic/MCP PRs)"]
        IMPA["Self-Improve (Eval Agent: Drift -> Retrain / Prompt Tune -> Canary)"]
    end

    subgraph GOV["7. ZERO-TRUST GOVERNANCE & RESPONSIBLE AI (NIST SP 800-207 / NCA ECC)"]
        IDP["Identity Plane: OAuth2/OIDC (Ping / Keycloak) + SPIFFE/SPIRE"]
        POL["Policy Plane: Apache Ranger (Data) + OPA (API/MCP/Agent) + Automated DLP"]
        CAT["DataHub (Active Metadata) + AsyncAPI Event Catalog-as-Code + Audit Ledger"]
    end

    SRC_DB --> CDC --> KAFKA
    SRC_DB --> ODS
    SRC_EVT --> KAFKA
    SRC_API --> APIGEE --> DLT
    SRC_B2B --> MFT --> OBJ
    KAFKA --> FLINK --> ICEBERG
    DLT --> ICEBERG
    ODS --> ICEBERG
    ICEBERG --- OBJ
    LAKEFS --- OBJ
    POLARIS --> ICEBERG
    GRAV --> POLARIS
    GRAV --> KAFKA
    OBJ --> KB --> VEC
    ICEBERG --> SPARK --> DBT --> ICEBERG
    ICEBERG --> TRINO --> SEM
    SEM --> BI
    SEM --> EXCH
    SEM --> MCP
    ICEBERG --> FEAST --> KSERVE
    VEC --> MCP
    MLFLOW --> KSERVE
    MCP <--> AGENTS
    KSERVE <--> AGENTS
    AGENTS --> CONV
    TRINO --> DS

    OBS --> OPSA --> SPARK
    AIOBS --> HEALA --> ORCH
    CAT --> EVOLVA --> DBT
    AIOBS --> IMPA --> MLFLOW
    GOV -. "Credential Vending & Masking" .-> L2
    GOV -. "Scoped Agent AuthZ & Guardrails" .-> MCP
```

---

## Core Architectural Pillars

### 1. Six Autonomous "Self-X" Control Loops
| Capability | Trigger Signals | Autonomous Action | Human-in-the-Loop (HITL) Gate |
| :--- | :--- | :--- | :--- |
| **Self-Operate** | Iceberg small-file ratio, query latency, storage heat | Automated Iceberg compaction, Z-order/liquid clustering, snapshot expiration, cold tiering | Cost-ceiling policy via OPA |
| **Self-Heal** | Soda v4 contract failure, schema drift, Evidently anomaly | Isolates data on Iceberg **WAP branch**, quarantines bad records, proposes schema cast, replays Kafka DLQ via Temporal | Auto-heal for additive/quarantine rules; PR approval for breaking schema changes |
| **Self-Evolve** | New AsyncAPI spec or Schema Registry version | Scaffolds Bronze/Silver SQLMesh/dbt models, ODCS data contracts, semantic KPIs, and MCP tool stubs | Architecture & Domain Steward PR review |
| **Self-Improve** | Langfuse faithfulness/latency drop or Evidently model drift | Triggers Feast feature refresh, MLflow retraining or RAG/prompt sweep, evaluates shadow KServe canary | Automated promotion only if statistical uplift & fairness gates pass |
| **Self-Govern** | Access requests, PII discovery, agent tool invocation | Automated DLP tagging, Ranger row/column masking, Polaris short-lived credential vending, OPA MCP guardrails | Policy-as-code review via GitOps |
| **Self-Scale** | Kafka consumer lag, Trino queue depth, GPU TTFT | KEDA autoscaling for Flink/workers, Spark dynamic allocation, KServe/vLLM GPU scale-to-zero & burst | Budget quota enforcement |

### 2. Five Enterprise AI Use-Case Archetypes Supported
1. **Analytical AI** — Prediction, classification, anomaly detection (`Spark`, `Feast`, `MLflow`, `Triton/ONNX`).
2. **Generative AI** — Summarization, RAG, conversational BI, multilingual content (`Document AI/OCR`, `Qdrant`, `vLLM`, `Langfuse`).
3. **Perception AI** — OCR, NLP/NLU, speech-to-text/TTS, computer vision, IoT/sensor (`Ray`, `LakeFS` multimodal corpora, `KServe`).
4. **Autonomous AI** — Multi-step agentic workflows and event-driven automation (`LangGraph`, `Temporal`, `MCP/A2A Gateway`).
5. **Decision AI** — Recommendations, simulations, policy/rules and optimization engines (`Semantic Layer`, `StarRocks`, `Decision APIs`).

### 3. Critical 2026 Lifecycle Decisions (Why This Differs From Legacy Diagrams)
- **Replaced MinIO Community Edition -> Apache Ozone / Ceph RGW** ([ADR-001](docs/adr/ADR-001-object-storage-ozone-ceph-over-minio-ce.md)): MinIO CE was archived in 2026 with unpatched CVEs and removed anonymous container pulls.
- **Replaced WhyLabs -> Langfuse + Evidently AI** ([ADR-004](docs/adr/ADR-004-ai-observability-langfuse-evidently-over-whylabs.md)): WhyLabs discontinued commercial operations in 2026; dual open-source observability covers both classical ML drift and LLM/agent traces.
- **Replaced n8n for Analytical ELT -> dlt / Debezium Kafka Connect** ([ADR-006](docs/adr/ADR-006-event-backbone-kafka-cdc-dlt-over-n8n.md)): Workflow tools lack schema contracts, CDC checkpointing, and bulk throughput.
- **Added Governed Semantic Layer + Federated Metalake (Gravitino + Polaris)** ([ADR-002](docs/adr/ADR-002-federated-metalake-gravitino-plus-polaris.md), [ADR-005](docs/adr/ADR-005-semantic-layer-and-governed-mcp-gateway.md)): Prevents KPI drift across BI tools and eliminates LLM SQL hallucinations.

---

## Repository Structure

```text
Agentic-Data-Platform/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── docker-compose.local.yml
├── docs/
│   ├── architecture/
│   │   ├── 01-system-context-and-layers.md
│   │   ├── 02-self-x-autonomous-control-plane.md
│   │   ├── 03-zero-trust-responsible-ai-governance.md
│   │   ├── 04-component-benchmark-and-market-analysis.md
│   │   └── 05-hybrid-sovereign-vs-cloud-mapping.md
│   └── adr/
│       ├── ADR-001-object-storage-ozone-ceph-over-minio-ce.md
│       ├── ADR-002-federated-metalake-gravitino-plus-polaris.md
│       ├── ADR-003-versioning-iceberg-wap-vs-lakefs.md
│       ├── ADR-004-ai-observability-langfuse-evidently-over-whylabs.md
│       ├── ADR-005-semantic-layer-and-governed-mcp-gateway.md
│       └── ADR-006-event-backbone-kafka-cdc-dlt-over-n8n.md
├── contracts/
│   ├── data-contracts/
│   │   └── customer_claims_gold.odcs.yaml
│   └── event-catalog/
│       └── claims-events.asyncapi.yaml
├── platform/
│   ├── openshift-gitops/
│   │   └── keda-flink-autoscaler.yaml
│   ├── policies/opa/
│   │   └── mcp_agent_guardrails.rego
│   └── observability/
│       └── otel-collector-config.yaml
└── agents/
    ├── mcp-servers/
    │   └── lakehouse_mcp_server.py
    └── self-healing/
        └── wap_reliability_agent.py
```

---

## Quickstart (Local Architecture Sandbox)

```bash
# 1. Launch local Iceberg REST Catalog (Polaris), S3-compatible storage (SeaweedFS),
#    Trino query engine, OPA Policy Engine, Valkey online store, and OpenTelemetry Collector
docker compose -f docker-compose.local.yml up -d

# 2. Verify OPA MCP Agent Guardrail policy
curl -s -X POST http://localhost:8181/v1/data/aegislake/mcp/allow \
  -H "Content-Type: application/json" \
  -d '{"input":{"agent_role":"data_analyst_agent","tool":"query_semantic_kpi","contains_pii":false,"mutation":false}}'

# 3. Run the Self-Healing WAP Reliability Agent simulation
python3 agents/self-healing/wap_reliability_agent.py
```

---

## Author

**Ahmed Salem** — Enterprise Integration & Data Architect (API · Events · Lakehouse · Agentic AI)
- GitHub: [github.com/salemfcih/Agentic-Data-Platform](https://github.com/salemfcih/Agentic-Data-Platform)
- LinkedIn: [linkedin.com/in/ahmedmohamed-salem-89194697](https://linkedin.com/in/ahmedmohamed-salem-89194697)
