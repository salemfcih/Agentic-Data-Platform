# ADR-010: Resilience, Tenancy and Data Lifecycle Baseline

- **Status**: Proposed
- **Date**: 2026-11-28
- **Deciders**: To be assigned by maintainers
- **Related**: ADR-001 (Object Storage), ADR-002, ADR-008

## Context

The reference architecture describes capabilities but not how the platform survives
failure, how domains are isolated from each other, or how data leaves the platform at end
of life. For a regulated, national-scale estate these are the first questions a design
review asks. Three gaps stand out:

1. **Recovery.** The platform has many stateful components, most with their own backing
   database. Losing a catalog database can make intact data files unreadable.
2. **Tenancy.** Data contracts name a domain, but the architecture has no isolation model
   for domains, quotas or cost.
3. **Lifecycle.** The design relies on immutability (raw zone, event log, table snapshots,
   corpus versions, audit ledger). Privacy law commonly grants a right to erasure and
   limits retention. The two must be reconciled by design.

## Decision Drivers

- Recovery objectives must be stated per service class and proven by restore tests.
- One domain's workload or mistake must not degrade or expose another domain.
- Personal data must be removable from every copy, including derived ones, within a stated time.
- The baseline must be achievable on-premises without assuming a second cloud region.

## Considered Options (recovery topology)

| Option | Summary | Assessment |
| :--- | :--- | :--- |
| A. Single site with backups | Lowest cost | Long recovery time; acceptable only for the lowest service class |
| **B. Two sites, active-passive, asynchronous replication** | Warm standby with defined recovery order | **Chosen as the baseline** |
| C. Two sites, active-active | Lowest recovery time | High complexity for catalogs and stateful stream jobs; a later step for specific services |

## Decision

### 1. Service classes

Adopters set the numbers. The structure is mandatory; the values below are illustrative.

| Class | Examples | Recovery point (illustrative) | Recovery time (illustrative) |
| :--- | :--- | :--- | :--- |
| Critical | Identity, key management, event backbone, catalog, certified data products behind operational decisions | Minutes | Under 1 hour |
| Important | Query engines, semantic layer, feature serving, model serving | Under 1 hour | A few hours |
| Standard | Workbenches, experiment tracking, non-certified zones | 24 hours | Next business day |

### 2. State inventory

Each stateful component is listed with its backing store, backup method, replication
method and owner. At minimum: identity and secrets; key management; object storage; the
table catalog database; policy stores; the metadata catalog; the event backbone and
schema registry; orchestrator databases; model and prompt registry; feature online store;
vector and graph stores; the audit ledger.

**Catalog and object storage are recovered as a pair.** A catalog restored to a point
earlier than the data files, or later, can point at metadata that does not exist. The
recovery procedure defines how the two are brought to a consistent point.

### 3. Recovery order

Identity and key management, then object storage, then catalog, then event backbone and
schema registry, then compute engines, then semantic layer and serving, then AI runtime.
Stream processors resume from replicated checkpoints or from a defined replay position.
Consumers of replicated topics must tolerate duplicates.

### 4. Proof

Restore and failover are tested on a schedule, per service class, with results recorded.
An untested backup is treated as no backup.

### 5. Tenancy

The **domain** is the unit of isolation.

| Layer | Isolation per domain |
| :--- | :--- |
| Catalog | Own namespace; ownership and grants scoped to it |
| Event backbone | Topic prefix; produce and consume rights scoped to it |
| Compute | Own Kubernetes namespace, resource quota, priority class and network policy |
| Object storage | Own bucket or prefix with separate credentials |
| AI runtime | Own agent namespace, tool allow-list and token budget |
| Cost | Mandatory labels for attribution of compute, storage, GPU and tokens |

Shared services (catalog, backbone, gateway) enforce per-domain rate limits and quotas so
one domain cannot starve others.

### 6. Environments

Development, test and production are separate. Production data does not enter lower
environments unless masked or synthetic. Promotion of pipelines, policies, contracts and
models between environments happens through version control, never by manual change in
production.

### 7. Data lifecycle and erasure

- Every asset has a retention period derived from its classification and legal basis,
  recorded in its contract.
- An erasure request is executed by a documented procedure that covers every copy:

| Location | Erasure mechanism |
| :--- | :--- |
| Raw and curated tables | Row-level delete, then expiry of snapshots that still contain the data |
| Event log | Tombstones on compacted topics, or per-subject encryption keys destroyed on request |
| Vector and graph stores | Delete derived chunks and entities; re-index |
| Unstructured corpora | Delete the object and run garbage collection on old versions |
| Features and model inputs | Delete from offline and online stores; record whether retraining is required |
| Audit ledger | Stores references and hashes, not raw personal data, so the ledger stays immutable |
| Telemetry and traces | Redact personal data at collection; short retention |

- The procedure has a stated completion time and produces evidence of completion.
- "Immutable" in this architecture means "not silently changed". It does not mean "kept forever".

### 8. Keys, secrets and egress

- Encryption keys are held in a key management service with rotation; data at rest and in
  transit is encrypted.
- Secrets are issued dynamically where possible. Example configurations in this repository
  must not contain real or default credentials.
- Agent runtimes have deny-by-default network egress.
- A routing rule decides which data classifications may be sent to which model endpoints.
  `confidential` and `restricted` content stays on sovereign endpoints unless an explicit,
  recorded exception exists.

## Consequences

**Positive**
- Recovery, isolation and erasure become stated properties with tests behind them.
- The largest hidden risk, catalog and storage diverging, is addressed explicitly.
- Cost and noisy-neighbour problems are attributable to a domain.

**Negative / costs**
- A second site and replication roughly double infrastructure for critical services.
- Per-domain isolation increases the number of namespaces, credentials and quotas to manage.
- Erasure across derived stores requires lineage that is complete enough to find every copy.
- Per-subject key destruction on the event log adds key-management load.

## Open Questions

- Which components can be consistently recovered together, and what is the practical
  recovery point for the catalog and storage pair?
- How is GPU capacity shared and reserved across domains and across sites?
- What evidence format satisfies an auditor that erasure reached every derived store?
