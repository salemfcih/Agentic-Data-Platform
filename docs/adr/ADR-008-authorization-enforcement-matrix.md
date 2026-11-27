# ADR-008: One Policy Source, an Explicit Enforcement Matrix, and Trusted Access Paths

- **Status**: Proposed
- **Date**: 2026-11-28
- **Deciders**: To be assigned by maintainers
- **Related**: ADR-002 (Polaris + Gravitino), ADR-005, ADR-007, ADR-009

## Context

The reference architecture contains many components that each make authorization
decisions: the Iceberg REST catalog, the fine-grained data policy engine, the federated
metalake, the event backbone, the semantic layer, the OLAP engine, the vector store, the
graph store, the feature store and the MCP gateway policy engine.

ADR-002 states that the metalake removes authorization split-brain. That is a goal, not
yet a design. Two concrete problems remain:

1. **Credential vending is table-scoped.** A catalog can issue short-lived storage
   credentials for a table. Any client holding them reads the files directly. Row filters
   and column masks exist only if the *engine* applies them. A notebook or a distributed
   Python job reading Iceberg files with vended credentials sees every row and column.
2. **Non-tabular stores are outside the tabular policy engine.** Document chunks in a
   vector store, entities in a graph, events on a topic and features in an online store
   each need an enforcement point, or sensitive data leaks through the side door.

## Decision Drivers

- A data owner should express a rule once and be able to see where it is enforced.
- Sensitive data must not be readable through a path that cannot enforce its policy.
- Unknown or unclassified data must fail closed.
- The design must be testable: each claim of enforcement needs an automated check.

## Considered Options

| Option | Summary | Why not chosen |
| :--- | :--- | :--- |
| A. Each store manages its own policy | Simple to start | Guaranteed drift; nobody can state the effective policy |
| **B. One authoring source, push-down where supported, explicit matrix, trusted paths for sensitive data** | Policy as code, with a published table of who enforces what | **Chosen** |
| C. All access through a single SQL gateway | Strongest control | Blocks legitimate batch, ML and streaming paths; not realistic as the only rule |

Option B borrows from C: for the most sensitive classes, only trusted paths are allowed.

## Decision

### 1. Classification drives policy

Every asset (table, column, topic, document collection, feature view, model) carries a
classification tag in the catalog. This reference uses four tiers as placeholders:
`public`, `internal`, `confidential`, `restricted`. Adopters map them to their own scheme.

**An asset with no classification is treated as `restricted`.** New columns are masked
until classified (see ADR-009, fail-closed invariant).

### 2. One authoring source

Data policy is authored once, as code in Git, in terms of classification tags, subject
attributes and purpose. It is distributed to enforcement points by push-down or sync. A
scheduled drift check compares the intended policy with the effective grants in each
engine and raises an incident on any difference.

### 3. Enforcement matrix

The matrix is a required, versioned artifact. The table below is the starting template.
Each cell must be verified for the specific engine and version an adopter runs, then
backed by a conformance test.

| Access path | Table / object level | Row filter | Column mask | Enforced by | Allowed classifications |
| :--- | :--- | :--- | :--- | :--- | :--- |
| SQL through a trusted query engine | Yes | Yes | Yes | Engine policy plug-in, subject from ADR-007 | All |
| Semantic layer / metrics API | Yes | Yes (delegated) | Yes (delegated) | Passes the subject to the trusted engine; holds no broad credential | All |
| Batch or stream job on a trusted, locked-down cluster | Yes | To verify per engine | To verify per engine | Engine plug-in; no user code with raw storage access | Up to the verified level |
| Direct table read with vended storage credentials (notebooks, Python, distributed ML) | Yes | **No** | **No** | Catalog only | `public`, `internal`, or pre-masked copies |
| Event topics | Topic level | No | No (use field-level encryption or tokenization at produce time) | Broker authorization | Per topic classification |
| Vector / hybrid retrieval | Collection level | Yes, as a mandatory metadata filter | Not applicable | Retrieval service, never the agent | All, if chunk ACLs are present |
| Graph store | Database / label level | To verify | To verify | Retrieval service | Up to the verified level |
| Online feature store | Feature view level | No | No | Feature service | Features derived from sensitive data inherit its class |
| Unstructured object corpora | Prefix / repository level | Not applicable | Not applicable | Object store and versioning layer | Per corpus classification |
| MCP tools | Tool level | Through the path the tool uses | Through the path the tool uses | Gateway policy engine (OPA) | Per tool registry entry |

### 4. Trusted access paths

- For `confidential` and `restricted` data, the catalog issues storage credentials only to
  registered trusted engine principals. Humans, notebooks and general-purpose jobs do not
  receive them.
- Paths that cannot enforce row or column policy get masked or aggregated copies,
  published as separate data products with their own contracts.

### 5. Retrieval-time access control

- Every chunk inherits the access control list of its source document at index time.
- The retrieval service applies the subject's entitlements as a server-side filter on
  every query. An agent cannot remove or widen the filter.
- A chunk with no ACL is not returned.
- When a source document's ACL changes, its chunks are re-indexed or invalidated within a
  stated time bound.

### 6. Conformance tests

For each row of the matrix, an automated test attempts to read a known `restricted`
column and a row outside the test subject's entitlement. The test must fail to read them.
These tests run in CI for policy changes and on a schedule in each environment.

## Consequences

**Positive**
- The effective policy can be stated and audited: one source, one matrix, tests per path.
- The direct-read bypass is closed by rule instead of by assumption.
- Retrieval for AI is governed by the same classification as tables.

**Negative / costs**
- Data scientists lose direct file access to sensitive tables and need masked copies.
- Masked copies add storage and pipeline work.
- The drift checker and conformance tests are new components to build and maintain.
- Push-down support differs by engine and version; some cells will be "not supported" and
  must be handled by restricting the path.

## Open Questions

- Which engines in the reference stack can verifiably enforce row and column policy for
  batch and streaming jobs, at which versions?
- How is purpose (why the data is being accessed) represented and checked?
- What is the acceptable delay between an ACL change and re-indexing of affected chunks?
