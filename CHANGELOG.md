# Changelog

## Unreleased

### Added
- ADR-007 to ADR-010 (status Proposed): agent identity and delegated authority; policy
  source and enforcement matrix; autonomy levels and Self-X safety; resilience, tenancy
  and data lifecycle.
- Policy tests (`platform/policies/opa/mcp_agent_guardrails_test.rego`) and policy data
  (`platform/policies/opa/data.json`: tool registry, catalog classifications, controls).
- `platform/openshift-gitops/flink-claims-iceberg-sink.yaml`: stream job using the Flink
  Kubernetes Operator autoscaler.
- `docs/architecture/aegislake-architecture.svg`: static export of the architecture diagram.
- `.env.example` for local sandbox secrets.
- "Alternatives Considered" sections in ADR-001 to ADR-006.

### Changed
- **Agent guardrail policy rewritten.** Tool risk comes from the registry and data
  sensitivity from the catalog, not from the caller. A missing token estimate is a deny.
  Publishing needs a second identity. A kill switch stops autonomous writes. Unclassified
  data is treated as restricted. The decision endpoint is now
  `v1/data/aegislake/mcp/decision` and takes a new input shape (see the README quickstart).
- **Tool gateway example** (`agents/mcp-servers/lakehouse_mcp_server.py`) builds the policy
  input from trusted sources, calls OPA, and denies when OPA is unreachable.
- **Self-healing example** (`agents/self-healing/wap_reliability_agent.py`) reads
  `completenessRequired` from the data contract, never publishes its own fix, and holds
  partial data when the contract requires completeness.
- **Data contract** now validates against the ODCS v3.1.0 schema. `claim_amount_sar` became
  `claim_amount` plus `currency_code`, and `feature_date` was added to the key.
- **Event specification** now describes the payload as an Avro schema, matching its
  declared content type.
- **Autoscaling manifests.** `keda-flink-autoscaler.yaml` was replaced by
  `keda-kafka-consumer-autoscaler.yaml`, which targets an ordinary consumer Deployment.
- **Telemetry config** separates general traces from LLM traces and masks personal data
  at collection.
- **Local sandbox** no longer contains a default credential.
- **Architecture diagram** updated for ADR-007 to ADR-010.
- **Documentation wording.** Absolute claims replaced with mechanisms or measurable
  statements. Portability is described as portable interfaces, not portable workloads.

### Fixed
- WhyLabs discontinued commercial operations in early 2025, not 2026 (README, ADR-004,
  component benchmark).
- MinIO timeline in ADR-001 corrected to the publicly documented sequence.

### Known gaps
- `opa test` has not been run on the policy test file. The policy itself was evaluated
  against all 21 test scenarios with a Rego interpreter library.
- The telemetry config and the Flink and KEDA manifests have not been applied to a running
  collector or cluster.
- The local sandbox services are not connected to each other, and image tags are not pinned.
- No CI yet for policy tests and contract validation.
- No threat model and no control mapping for the cited standards.
