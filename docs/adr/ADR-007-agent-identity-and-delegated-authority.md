# ADR-007: Agent Identity and Delegated Authority (Subject, Actor, Task)

- **Status**: Proposed
- **Date**: 2026-11-28
- **Deciders**: To be assigned by maintainers
- **Related**: ADR-005 (Semantic Layer and MCP Gateway), ADR-008, ADR-009

## Context

The architecture gives every agent pod a workload identity (SPIFFE/SPIRE) and routes
tool calls through a policy-enforced MCP gateway. That answers "which workload is
calling?" It does not answer "on whose behalf, and for what task?"

When a copilot answers a question for a human, the call chain is:

`user -> agent -> MCP gateway -> MCP server -> semantic layer -> query engine`

If the engine only sees the agent's service identity, row filters and column masks are
evaluated for the agent, not for the person asking. Two users with different
entitlements get the same answer. This is the confused-deputy problem, and it is the
most common way an agent leaks data it was technically "allowed" to read.

The MCP authorization specification treats a protected MCP server as an OAuth 2.1
resource server. Tokens must be bound to the server they were issued for, and passing a
client's token through to an upstream API is not permitted. The design below follows
that model.

## Decision Drivers

- Data policy must be evaluated for the human (or accountable system principal), not for the agent.
- An agent must never hold more authority than the principal it acts for.
- A stolen or replayed token must be useless outside its intended server and task.
- Every action must be attributable to a subject, an actor and a task in the audit trail.
- The design must work for both interactive and fully autonomous (no human present) loops.

## Considered Options

| Option | Summary | Why not chosen |
| :--- | :--- | :--- |
| A. Agent service identity only | Agent calls everything with its own identity | Confused deputy; data policy cannot follow the user |
| B. Pass the user's token through | Agent forwards the user's access token downstream | Token is not audience-bound; forbidden by the MCP spec; a compromised tool can replay it |
| **C. Token exchange with an actor claim** | Exchange the user's token for a short-lived, audience-bound, task-scoped token that names both user and agent | **Chosen** |
| D. One agent instance per user with the user's credentials | Agent runs "as" the user | No distinction between user and agent in audit; unbounded authority; hard to operate |

## Decision

Every tool call carries three identities, and policy is evaluated on all three.

| Identity | Meaning | Source of truth |
| :--- | :--- | :--- |
| **Subject** | The human, or the accountable system principal for autonomous loops | Identity provider (OIDC) |
| **Actor** | The agent workload making the call | SPIFFE SVID |
| **Task** | The unit of work: id, purpose, autonomy level (ADR-009), expiry | Issued by the orchestrator when the task starts |

Rules:

1. **Token exchange per hop.** The gateway exchanges the caller's token (OAuth 2.0 Token
   Exchange, RFC 8693) for a new token whose `sub` is the subject, whose `act` claim is the
   agent's SPIFFE ID, and whose `aud` is exactly one MCP server (Resource Indicators,
   RFC 8707). An MCP server that needs to call upstream performs its own exchange. Tokens
   are never forwarded as-is.
2. **Short-lived and task-scoped.** Exchanged tokens live for minutes, carry only the
   scopes needed for the tools in the task plan, and include the task id.
3. **Effective permission is an intersection.** A call is allowed only if the subject is
   entitled to the data, the actor is permitted to use the tool, and the task scope
   includes the action. No hop can add authority.
4. **Engines evaluate data policy against the subject.** The semantic layer and query
   engines receive the subject identity and apply row filters and masks for that subject
   (see ADR-008 for which access paths can do this).
5. **Autonomous loops use named system principals.** A Self-X loop has no human subject.
   Its subject is a system principal owned by a named team, with a maximum autonomy level
   and a narrow entitlement set. It is never a shared "platform admin" identity.
6. **Agent-to-agent hand-offs extend the chain, bounded.** Each hop nests the previous
   actor in the `act` claim. Chains have a maximum depth, and the receiving agent's
   authority is again the intersection in rule 3.
7. **Policy inputs are built by the gateway.** Subject, actor, task and resource attributes
   passed to OPA come from validated tokens, the tool registry and the catalog. Nothing an
   agent places in tool arguments is treated as a fact about risk or sensitivity.
8. **Audit.** Each decision is logged with subject, actor chain, task id, tool, resource,
   policy decision and reasons.

## Consequences

**Positive**
- Row-level and column-level policy follows the person asking, including through agents.
- A leaked token is limited to one server, one task and a few minutes.
- Audit can answer "who asked, which agent acted, under which task" for every call.

**Negative / costs**
- The identity provider must support token exchange and custom claims. This must be
  verified for each candidate IdP before adoption.
- Each engine must accept a JWT and map the subject to its policy principal. Paths that
  cannot do this are restricted by ADR-008.
- Extra token round-trips add latency. Mitigation: cache exchanged tokens per task and audience.
- More moving parts to test and operate.

## Validation (acceptance tests)

- The same question asked by two users with different row entitlements returns different rows.
- A token issued for MCP server A is rejected by MCP server B.
- A token is rejected after the task expires, and after the task is cancelled.
- An agent cannot invoke a tool outside the task scope even if its role permits the tool.
- A three-hop agent chain produces an audit record naming all three actors and the original subject.

## Open Questions

- Which claims carry group membership and clearance, and how large may the token become?
- How are long-running tasks (hours or days) re-authorized without long-lived tokens?
- How is consent captured when an agent acts for a user in a system the user has never used?
