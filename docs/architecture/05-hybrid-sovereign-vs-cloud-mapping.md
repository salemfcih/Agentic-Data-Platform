# 05 — Dual Deployment Mapping (Sovereign On-Premises vs. Cloud-Native) & MLOps Stack Canvas

Regulated enterprises face a classic tension: **sovereign, classified data requires strict on-premises residency**, while **advanced GenAI and elastic analytics benefit from managed cloud velocity**. AegisLake resolves this via a **Hybrid Sovereign-First Architecture** where logical layers, ODCS data contracts, AsyncAPI events, and MCP interfaces remain identical across both deployment planes.

> **What is portable:** the interfaces. Contracts, event specifications, the Iceberg REST protocol and MCP tool definitions carry across. **What is not:** the workloads. Stream jobs, SQL dialects, orchestration and agent runtimes differ between the two columns below and need re-platforming. The table maps capabilities. It does not list drop-in replacements. Which data classifications may leave the sovereign plane at all is decided by the routing rule in [ADR-010](../adr/ADR-010-resilience-tenancy-and-data-lifecycle.md).

---

## Side-by-Side Technology Mapping

| Logical Capability | Sovereign On-Premises Stack (OpenShift / OSS) | Managed Cloud-Native Stack (GCP Reference Blueprint) | Interoperability Standard |
| :--- | :--- | :--- | :--- |
| **API Gateway & Dev Portal** | Google Apigee Hybrid / Kong Enterprise | Apigee API Platform + Developer Portal + Cloud Endpoints | OpenAPI 3.1, OAuth2/OIDC, mTLS |
| **Event Backbone & Routing** | Confluent Platform (CFK) / Strimzi Kafka | Cloud Pub/Sub + Eventarc | AsyncAPI 3.0, CloudEvents, Avro/JSON |
| **Managed CDC** | Debezium + Kafka Connect | Datastream (Oracle/Postgres/MySQL) | Debezium Envelope / Avro Schema |
| **Batch & Stream Processing** | Apache Spark + Apache Flink (K8s Operator) | Cloud Dataflow (Apache Beam) + Dataproc | Apache Iceberg v3, OpenLineage |
| **SQL Transforms & Modeling** | SQLMesh / dbt Core (Medallion / Data Vault 2.0) | Dataform / dbt Core | ANSI SQL, GitOps |
| **Operational Data Store (ODS)** | PostgreSQL / Distributed SQL + MDM | Cloud SQL / Spanner + Bigtable (sub-ms) | JDBC/REST, Canonical Entity Contracts |
| **Object Storage & Lakehouse** | Apache Ozone / Ceph RGW + Apache Iceberg | Cloud Storage (GCS) + BigQuery (BigLake Iceberg) | S3 API, Apache Iceberg Table Spec |
| **Catalog & Data Fabric** | Apache Polaris + Apache Gravitino + DataHub + Trino | Dataplex Universal Catalog + Data Lineage API + Analytics Hub + Denodo | Iceberg REST Spec, OpenLineage |
| **Privacy & DLP** | Microsoft Presidio + Apache Ranger + OPA | Sensitive Data Protection (Cloud DLP) + Cloud IAM + VPC-SC | Policy-as-Code, Tag-Based Masking |
| **Semantic Layer & BI** | Cube / dbt MetricFlow + Apache Superset / Power BI | Looker (LookML Metrics Layer) + Looker Studio / Tableau + BI Engine | Governed KPI YAML / SQL API |
| **AI Workbench** | JupyterHub / Marimo + OpenShift Dev Spaces | Vertex AI Workbench + Colab Enterprise + BigQuery ML | OCI Containers, Python/PyTorch/JAX |
| **Feature Store** | Feast (Iceberg Offline + Valkey Online) | Vertex AI Feature Store (BigQuery Offline) | Point-in-Time Feature Contracts |
| **GenAI, RAG & Agents** | Document OCR + Qdrant + LangGraph + MCP Gateway + vLLM | Document AI + Vector Search + Vertex AI Agents + Model Garden + Dialogflow CX | Model Context Protocol (MCP) & A2A |
| **Model Serving & MLOps** | MLflow 3.x + KServe (vLLM + Triton/ONNX) + Airflow 3.x | Vertex AI Registry/Pipelines/Endpoints + Cloud Run / GKE + Cloud Composer | OCI Model Images, CI/CT/CD |
| **Observability & Eval** | OpenTelemetry + Grafana LGTM + Evidently AI + Langfuse | Cloud Monitoring + Vertex AI Evaluation & Explainability | OTLP, OpenTelemetry GenAI Semantic Conventions |

---

## MLOps Transformational Maturity & Stack Canvas

AegisLake targets the **Transformational MLOps Maturity Stage** (fully automated **CI/CT/CD** with reusable shared platform services, moving past ad-hoc *Tactical* pilots and partially automated *Strategic* pipelines):

| Stack Canvas Pillar | AegisLake Architectural Guarantee |
| :--- | :--- |
| **Value Proposition** | Every AI initiative links to one of the 5 AI Archetypes and passes Use-Case Risk Classification before compute provisioning. |
| **Data Sources & Versioning** | Immutable Bronze ingestion + Iceberg Snapshot IDs (tabular) + LakeFS commit hashes (unstructured) make every training dataset reproducible by reference. |
| **Data Analysis & Experiment Mgmt** | Isolated AI Workbench sandboxes logging parameters, metrics, prompts, and datasets automatically to `MLflow 3.x`. |
| **Feature Store & Workflows** | Centralized `Feast` definitions computed from one definition via Spark (offline) and Flink (online) to reduce training-serving skew. |
| **CI/CT/CD Pipeline Orchestration** | GitOps triggers automated unit tests, bias/fairness checks, shadow canary deployment, and scheduled/drift-triggered retraining. |
| **Model Registry & Serving** | Versioned OCI model artifacts promoted across Dev -> Staging -> Prod on `KServe` (`<50ms` real-time SLA + batch scoring). |
| **Monitoring & Maintenance** | Continuous data drift (`Evidently`), GenAI faithfulness/cost (`Langfuse`), and automated Self-Improve retraining loops. |
