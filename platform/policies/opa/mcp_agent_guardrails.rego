# AegisLake MCP agent guardrails (see ADR-007 and ADR-009).
#
# Design rules:
#   - Facts about a tool (effect, risk, reversibility, allowed roles) come from the
#     reviewed tool registry in `data`, not from the caller.
#   - Data sensitivity comes from the catalog in `data`. Unclassified means restricted.
#   - The token estimate is mandatory. A missing value is a deny, not a pass.
#   - Read tools check the actor's role.
#   - Publishing needs a second identity (proposer is not approver).
#   - A kill switch stops all autonomous writes.
#   - Autonomy levels decide between "act" and "ask a human".
#
# Trusted input, built by the gateway from validated tokens and its own lookups:
#   input.subject.id, input.subject.clearance      who the call is for
#   input.actor.spiffe_id, input.actor.role        which agent workload is calling
#   input.task.id, input.task.autonomy_level       the unit of work and its granted level
#   input.tool.name                                the requested tool
#   input.resource.name                            the target asset, resolved by the gateway
#   input.request.estimated_tokens                 gateway estimate for this call
#   input.request.proposer_spiffe_id               who prepared the change being published
#
# Nothing in the tool-call arguments written by the agent is read by this policy.

package aegislake.mcp

import rego.v1

default allow := false

default require_hitl := false

# ---------------------------------------------------------------------------
# Facts from the registry, the catalog and platform controls
# ---------------------------------------------------------------------------

# Undefined for a tool that is not in the registry, which denies everything below.
tool := data.aegislake.registry.tools[input.tool.name]

default classification := "restricted"

classification := c if {
	c := data.aegislake.catalog.assets[input.resource.name].classification
}

default masking_enforced := false

masking_enforced if {
	data.aegislake.catalog.assets[input.resource.name].masking_enforced == true
}

default kill_switch := false

kill_switch if {
	data.aegislake.controls.kill_switch == true
}

default max_tokens := 50000

max_tokens := n if {
	n := data.aegislake.controls.max_tokens_per_call
}

sensitive_classes := {"confidential", "restricted"}

# Which subject clearances may read which sensitive class.
cleared_for := {
	"confidential": {"confidential", "restricted"},
	"restricted": {"restricted"},
}

# ---------------------------------------------------------------------------
# Checks shared by reads and writes
# ---------------------------------------------------------------------------

task_bound if {
	is_string(input.task.id)
	input.task.id != ""
}

role_permitted if {
	input.actor.role in tool.allowed_roles
}

within_budget if {
	is_number(input.request.estimated_tokens)
	input.request.estimated_tokens >= 0
	input.request.estimated_tokens <= max_tokens
}

common_checks if {
	task_bound
	role_permitted
	within_budget
}

# ---------------------------------------------------------------------------
# Data access: sensitivity is decided by the catalog, not by the caller
# ---------------------------------------------------------------------------

data_access_ok if {
	tool.touches_data == false
}

data_access_ok if {
	tool.touches_data == true
	not classification in sensitive_classes
}

data_access_ok if {
	tool.touches_data == true
	classification in sensitive_classes
	input.subject.clearance in cleared_for[classification]
	masking_enforced
}

# ---------------------------------------------------------------------------
# Autonomous writes (ADR-009)
# ---------------------------------------------------------------------------

autonomous_ok if {
	tool.risk == "low"
	tool.reversible == true
	tool.max_autonomy_level >= 3
	input.task.autonomy_level >= 3
}

second_party_required if {
	tool.requires_second_party == true
}

separation_ok if {
	not second_party_required
}

separation_ok if {
	second_party_required
	is_string(input.request.proposer_spiffe_id)
	input.request.proposer_spiffe_id != ""
	input.request.proposer_spiffe_id != input.actor.spiffe_id
}

# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------

# Reads.
allow if {
	tool.effect == "read"
	common_checks
	data_access_ok
}

# Writes that may run without a human.
allow if {
	tool.effect == "write"
	common_checks
	not kill_switch
	autonomous_ok
	separation_ok
}

# A permitted actor asking for a write that cannot run autonomously goes to a human.
# An unknown tool, a wrong role or an unbound task is a plain deny.
require_hitl if {
	tool.effect == "write"
	task_bound
	role_permitted
	not allow
}

# ---------------------------------------------------------------------------
# Reasons, for the audit record and for the person reviewing an escalation
# ---------------------------------------------------------------------------

reasons contains "unknown_tool" if {
	not tool
}

reasons contains "task_not_bound" if {
	not task_bound
}

reasons contains "role_not_permitted" if {
	tool
	not role_permitted
}

reasons contains "token_estimate_missing_or_over_budget" if {
	not within_budget
}

reasons contains "classification_requires_clearance_and_masking" if {
	tool.effect == "read"
	not data_access_ok
}

reasons contains "kill_switch_active" if {
	tool.effect == "write"
	kill_switch
}

reasons contains "autonomy_level_insufficient" if {
	tool.effect == "write"
	not autonomous_ok
}

reasons contains "second_party_required" if {
	tool.effect == "write"
	not separation_ok
}

decision := {
	"allow": allow,
	"require_hitl": require_hitl,
	"reasons": reasons,
}
