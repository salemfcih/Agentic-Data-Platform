# 02 — The Autonomous "Self-X" Control Plane

Traditional data platforms degrade under entropy: small files accumulate, schemas break downstream dashboards, KPIs drift across teams, and ML models silently decay. **AegisLake** embeds six closed-loop cybernetic control planes powered by metadata, telemetry, and policy-bounded agents.

## Closed-Loop Architecture Pattern
Every Self-X loop follows a strict **Sense -> Diagnose -> Plan -> Policy-Gate -> Act -> Verify** cycle:
1. **Sense**: Continuous signals from OpenTelemetry, OpenLineage, Soda v4, Evidently AI, Langfuse, and Kafka Consumer Lag.
2. **Diagnose**: Specialized Platform Agent retrieves lineage from `DataHub`, schema diffs from `Schema Registry`, and table manifests from `Apache Polaris` via read-only **MCP Tools**.
3. **Plan**: Produces a deterministic remediation plan or GitOps Pull Request.
4. **Policy-Gate**: `OPA` evaluates facts from the tool registry and the catalog (tool risk, reversibility, data classification), the task's autonomy level and the kill switch to decide **Autonomous Execution** vs. **Human-in-the-Loop (HITL) Approval**. Risk attributes are never taken from the agent's own arguments.
5. **Act**: Executes through durable `Temporal` workflows or `ArgoCD` GitOps sync.
6. **Verify**: Confirms SLA/metric recovery, rolls back if the check fails, and writes an immutable audit record.

Autonomy ceilings per action, action budgets, separation of duties and the kill switch are defined in [ADR-009](../adr/ADR-009-autonomy-levels-and-self-x-safety.md).

---

## Sequence 1: Self-Healing Data Reliability Loop (Iceberg WAP + DLQ Replay)

```mermaid
sequenceDiagram
    participant P as Producer / Kafka
    participant F as Flink / Spark Job
    participant W as Iceberg WAP Branch
    participant DQ as Soda v4 + Evidently
    participant A as Self-Healing Agent
    participant OPA as OPA Policy Gate
    participant T as Temporal / GitOps
    participant PUB as Publisher Identity

    P->>F: Stream / Batch Records
    F->>W: Write to isolated WAP branch (main untouched)
    W->>DQ: Run ODCS Contract & Anomaly Checks
    alt Checks Pass
        DQ->>PUB: Checks passed, request publish
        PUB->>W: Fast-forward merge to main
    else Schema Break or Anomaly Detected
        DQ->>A: Emit OpenLineage FAIL + Contract Diff
        A->>A: Inspect Schema Registry diff & sample rows
        A->>OPA: Request remediation action (Quarantine vs Schema Cast)
        alt Low-Risk Policy Approved (Quarantine Bad Rows)
            OPA-->>A: ALLOW (Auto-Execute)
            A->>T: Quarantine malformed rows on the branch
            T->>PUB: Request publish if the contract allows partial data
            PUB->>W: Verify checks, publish, record incident
        else Breaking Structural Change
            OPA-->>A: REQUIRE_HITL
            A->>T: Open Git PR with dbt/ODCS fix + notify Domain Steward
        end
    end
```

---

## Detailed Specification of All Six Self-X Loops

### 1. Self-Operate (AIOps & FinOps Optimization)
- **Signals**: Iceberg manifest file counts, Trino/Spark spill metrics, object storage access frequency, idle GPU pods.
- **Actions**:
  - Schedules `rewrite_data_files` compaction and Z-order / liquid clustering only on tables exceeding fragmentation thresholds.
  - Expires obsolete Iceberg snapshots and removes orphan files per retention policy.
  - Dynamically tiers cold Bronze partitions to archival storage classes and surfaces per-domain FinOps chargeback reports.

### 2. Self-Heal (Zero-Downtime Data Reliability)
- **Signals**: ODCS contract failures (null spikes, type mismatches, referential breaks), Flink checkpoint failures, Airflow task crashes.
- **Actions**:
  - Keeps unverified data off Gold `main` by writing to an Iceberg Write-Audit-Publish (WAP) branch first. The agent that prepares a fix does not publish it.
  - Routes malformed payloads to typed Quarantine tables with full provenance. Compliant records are published on time only when the data contract allows partial data. Otherwise the branch is held until it reconciles with the source.
  - Orchestrates safe Kafka offset replay via Temporal once the fix merges.

### 3. Self-Evolve (Living Schemas, Contracts & Semantic Layer)
- **Signals**: New versioned specs merged in the `AsyncAPI` Event Catalog-as-Code repository or Schema Registry.
- **Actions**:
  - Auto-generates Bronze/Silver `SQLMesh/dbt` models, unit tests, and `ODCS v3` YAML data contracts.
  - Flags semantic KPI impacts across downstream dashboards and opens draft PRs updating `Cube/MetricFlow` definitions and governed `MCP Tool` schemas.
  - All output is pull requests for human review. Tools are never registered automatically.

### 4. Self-Improve (Closed-Loop ML & GenAI Optimization)
- **Signals**: `Evidently AI` covariate/concept drift, `Langfuse` faithfulness/hallucination/tool-accuracy degradation, user thumbs-down feedback.
- **Actions**:
  - Triggers automated `Feast` feature materialization and `MLflow` retraining pipelines (CI/CT/CD).
  - For GenAI/RAG agents, runs automated offline evaluation suites comparing candidate prompts, embedding models, or chunking strategies against golden datasets.
  - Deploys candidates as shadow/canary traffic on `KServe` and promotes only when accuracy, latency, token cost, and fairness thresholds beat the champion model.

### 5. Self-Govern (Autonomous Compliance & Zero-Trust Posture)
- **Signals**: New table/column creation in Polaris/Gravitino, unstructured document ingest, anomalous agent query volume.
- **Actions**:
  - Masks newly landed columns by default, then runs automated PII/PHI classification (`Presidio / Cloud DLP`) and tags assets in `DataHub`. Stricter `Apache Ranger` masking is applied automatically. Loosening a policy needs a person.
  - Revokes anomalous agent sessions via `OPA` and logs every prompt, retrieved citation, and tool call to an immutable audit ledger.

### 6. Self-Scale (Multi-Dimensional Elastic Compute)
- **Signals**: Kafka consumer lag, Trino queued query count, Spark pending shuffle stages, `vLLM` Time-To-First-Token (TTFT) & KV-cache saturation.
- **Actions**:
  - The Flink Kubernetes Operator autoscaler scales stream jobs. `KEDA` horizontally scales Kafka Connect workers, consumer services, and MCP servers based on event lag.
  - `KServe` scales GPU LLM replicas up during peak business hours and down to zero (or warm standby) off-peak.
