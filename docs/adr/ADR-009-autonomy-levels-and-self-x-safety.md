# ADR-009: Autonomy Levels and Safety Invariants for the Self-X Control Plane

- **Status**: Proposed
- **Date**: 2026-11-28
- **Deciders**: To be assigned by maintainers
- **Related**: ADR-003 (WAP), ADR-005, ADR-007, ADR-008

## Context

The Self-X loops (operate, heal, evolve, improve, govern, scale) can compact tables,
quarantine and publish data, open pull requests, change masking, promote models and
revoke sessions. Together they are the most privileged identities on the platform.

The current design gates each action with a policy check, but several weaknesses remain:

- Risk attributes such as blast radius and PII presence are supplied by the agent that
  wants to act.
- The agent that proposes a fix can also publish it.
- Self-Govern classifies first and masks second, so a missed classification exposes data.
- Self-Heal may publish a partial data set to a certified table, which silently changes
  totals for consumers that assume completeness.
- New tools can be registered automatically.
- There is no shared definition of how much autonomy any loop has, no action budget and no
  single way to stop all loops.

## Decision Drivers

- Autonomy must be an explicit, reviewable setting per loop and action, not an emergent property.
- A wrong autonomous action must be bounded in size and reversible.
- The controls that govern agents must not be changeable by agents.
- Failure must move the system toward more protection, not less.

## Considered Options

| Option | Summary | Why not chosen |
| :--- | :--- | :--- |
| A. Per-action policy check only (current) | Each call is allowed, denied or escalated | No shared autonomy model, no budgets, no stop control |
| **B. Autonomy levels + safety invariants + budgets + kill switch** | Explicit ceiling per action, with invariants enforced in policy | **Chosen** |
| C. Human approval for every write | Safest | Removes the benefit of the control plane; causes approval fatigue |

## Decision

### 1. Autonomy levels

| Level | Name | What the agent may do |
| :--- | :--- | :--- |
| L0 | Observe | Collect signals and report |
| L1 | Recommend | Produce a recommendation for a human |
| L2 | Propose | Prepare the change (branch, pull request, plan). A human applies it |
| L3 | Act within guardrails | Apply a reversible, bounded change. Humans review after the fact |
| L4 | Act broadly | Not permitted for production data or policy in this reference |

Each tool in the registry has a **maximum autonomy level**. Each task is granted a level
when it starts. An action runs without a human only when both are L3 and every invariant
below holds. Otherwise it is escalated or denied.

### 2. Starting ceilings

Adopters should begin lower and raise a ceiling only with evidence.

| Loop | Action | Ceiling | Condition |
| :--- | :--- | :--- | :--- |
| Self-Operate | Compaction, clustering | L3 | Within maintenance window and action budget |
| Self-Operate | Snapshot expiry, orphan cleanup | L2, then L3 | Never below the contract's retention floor |
| Self-Operate | Storage tiering | L3 | Reversible tiers only |
| Self-Heal | Quarantine rows on an audit branch | L3 | Main is untouched |
| Self-Heal | Publish a branch to main | L3 | Different identity than the one that prepared it; contract checks pass |
| Self-Heal | Publish partial data | L2 | L3 only if the contract states completeness is not required |
| Self-Heal | Replay from a dead-letter queue | L2 | L3 only if the consumer is declared idempotent |
| Self-Heal | Breaking schema change | L2 | Always a reviewed pull request |
| Self-Evolve | Scaffold models, contracts, metric definitions | L2 | Pull request only |
| Self-Evolve | Register or change an MCP tool | L2 | Never automatic |
| Self-Evolve | Change policy, guardrails or this table | L1 | Agents may not author these |
| Self-Improve | Trigger retraining or an evaluation run | L3 | Within compute budget |
| Self-Improve | Shadow or canary deployment | L3 | Traffic share capped |
| Self-Improve | Promote to full production | L2 for high-risk use cases, L3 otherwise | Evaluation and fairness gates pass |
| Self-Govern | Add a classification tag, tighten masking | L3 | Stricter direction only |
| Self-Govern | Remove a tag, loosen masking, grant access | L1 | Human decision |
| Self-Govern | Revoke an anomalous agent session | L3 | Fail-safe direction |
| Self-Scale | Scale within quota | L3 | Hard quota enforced outside the agent |

### 3. Safety invariants

1. **Server-side facts.** Tool effect, risk, reversibility and required approvals come from
   the tool registry. Data sensitivity comes from the catalog. Agent-supplied arguments are
   never used as facts about risk (see ADR-007, rule 7).
2. **Proposer is not approver.** The identity that prepared a change cannot publish it. A
   second identity, human or a separate verifier service, is required.
3. **Fail closed.** New columns are masked until classified. Unclassified assets are
   treated as `restricted` (ADR-008). An unavailable policy engine means deny. An approval
   that times out means deny.
4. **Reversible or not autonomous.** Only actions with a tested rollback may run at L3.
   The pre-change state (for tables, the snapshot id) is recorded before acting.
5. **Budgets.** Each loop has limits per time window on number of actions, rows or bytes
   affected, and cost. Exceeding a budget drops the loop to L1 and pages a human.
6. **Kill switch.** One control drops all loops to L1. It is checked on every decision,
   operated by humans, protected from agent modification and exercised on a schedule.
7. **Verify, then keep or roll back.** Every L3 action has a post-condition check. A failed
   check triggers the rollback and an incident.
8. **Controlled tool supply chain.** Tools enter the registry by reviewed pull request, are
   pinned to a version or digest, and their descriptions are treated as untrusted text.
9. **Untrusted content cannot steer writes.** Content retrieved from documents, tickets,
   web pages or other tools is data, not instruction. A task that has ingested untrusted
   content may not invoke write tools without human approval.
10. **Protected control repositories.** Policy, tool registry, autonomy ceilings and
    contracts live in repositories where agents have no merge rights and changes need
    named human owners.
11. **Completeness is a contract property.** A data contract states whether partial
    publication is acceptable. Certified financial or regulatory tables default to
    "complete or not published", with a reconciliation check against the source.

### 4. Human-in-the-loop design

An escalation states what will change, why, the affected scope, the rollback and the
deadline. Each action class has named approvers and a response-time target. Approval
volume is measured, because a queue nobody reads is not a control.

### 5. Measures

Autonomous actions per loop, rollback rate, budget breaches, approval latency,
false-quarantine rate, and time to stop all loops in a kill-switch drill.

## Consequences

**Positive**
- Autonomy becomes a reviewed configuration with evidence behind each increase.
- A faulty or manipulated agent is limited by budgets, separation of duties and rollback.
- The control plane cannot rewrite its own rules.

**Negative / costs**
- More human review early on, until ceilings are raised.
- The tool registry, budgets, verifier identity and kill switch must be built and operated.
- "Complete or not published" will delay some tables that would otherwise ship partial data.

## Follow-up

- Add a threat model that maps these invariants to the OWASP Top 10 for Agentic
  Applications and records residual risk per item.
- The reference policy (`platform/policies/opa/`), the tool gateway example and the
  self-healing example implement invariants 1, 2, 3, 6 and 11. Budgets, rollback
  verification and the protected control repositories are not implemented yet.
