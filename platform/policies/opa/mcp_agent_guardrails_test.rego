# Tests for mcp_agent_guardrails.rego.
# Run from this folder with:  opa test . -v
# The tests use the registry, catalog and controls in data.json.

package aegislake.mcp_test

import rego.v1

import data.aegislake.mcp as policy

analyst_read := {
	"subject": {"id": "user-1", "clearance": "internal"},
	"actor": {"spiffe_id": "spiffe://example.internal/ns/agents/sa/bi-copilot", "role": "data_analyst_agent"},
	"task": {"id": "task-001", "autonomy_level": 1},
	"tool": {"name": "query_semantic_kpi"},
	"resource": {"name": "gold.claims.claim_volume_by_region"},
	"request": {"estimated_tokens": 1200},
}

healer_write := {
	"subject": {"id": "svc-self-heal", "clearance": "confidential"},
	"actor": {"spiffe_id": "spiffe://example.internal/ns/platform/sa/self-heal", "role": "platform_self_healing_agent"},
	"task": {"id": "task-002", "autonomy_level": 3},
	"tool": {"name": "quarantine_invalid_records"},
	"resource": {"name": "gold.claims.claim_risk_features_daily"},
	"request": {"estimated_tokens": 800},
}

publisher_write := {
	"subject": {"id": "svc-publisher", "clearance": "confidential"},
	"actor": {"spiffe_id": "spiffe://example.internal/ns/platform/sa/publisher", "role": "platform_publisher_agent"},
	"task": {"id": "task-003", "autonomy_level": 3},
	"tool": {"name": "promote_wap_branch"},
	"resource": {"name": "gold.claims.claim_risk_features_daily"},
	"request": {
		"estimated_tokens": 500,
		"proposer_spiffe_id": "spiffe://example.internal/ns/platform/sa/self-heal",
	},
}

# --- Reads -----------------------------------------------------------------

test_read_internal_asset_allowed if {
	policy.allow with input as analyst_read
}

test_read_confidential_denied_without_clearance if {
	inp := object.union(analyst_read, {"resource": {"name": "gold.claims.claim_risk_features_daily"}})
	not policy.allow with input as inp
	"classification_requires_clearance_and_masking" in policy.reasons with input as inp
}

test_read_confidential_allowed_with_clearance_and_masking if {
	inp := object.union(analyst_read, {
		"subject": {"id": "user-2", "clearance": "confidential"},
		"resource": {"name": "gold.claims.claim_risk_features_daily"},
	})
	policy.allow with input as inp
}

test_read_restricted_denied_when_masking_not_enforced if {
	inp := object.union(analyst_read, {
		"subject": {"id": "user-3", "clearance": "restricted"},
		"resource": {"name": "bronze.claims.raw_submissions"},
	})
	not policy.allow with input as inp
}

test_unclassified_asset_treated_as_restricted if {
	inp := object.union(analyst_read, {"resource": {"name": "gold.claims.not_in_catalog"}})
	policy.classification == "restricted" with input as inp
	not policy.allow with input as inp
}

test_caller_cannot_declare_data_non_sensitive if {
	inp := object.union(analyst_read, {
		"resource": {"name": "gold.claims.claim_risk_features_daily"},
		"contains_pii": false,
		"blast_radius": "low",
	})
	not policy.allow with input as inp
}

test_read_denied_for_role_not_in_registry_entry if {
	inp := object.union(analyst_read, {"tool": {"name": "inspect_wap_branch"}})
	not policy.allow with input as inp
	"role_not_permitted" in policy.reasons with input as inp
}

test_missing_token_estimate_denied if {
	inp := object.union(object.remove(analyst_read, ["request"]), {"request": {}})
	not policy.allow with input as inp
	"token_estimate_missing_or_over_budget" in policy.reasons with input as inp
}

test_over_budget_denied if {
	inp := object.union(analyst_read, {"request": {"estimated_tokens": 50001}})
	not policy.allow with input as inp
}

test_unknown_tool_denied_without_escalation if {
	inp := object.union(analyst_read, {"tool": {"name": "drop_everything"}})
	not policy.allow with input as inp
	not policy.require_hitl with input as inp
	"unknown_tool" in policy.reasons with input as inp
}

test_unbound_task_denied if {
	inp := object.union(analyst_read, {"task": {"id": "", "autonomy_level": 1}})
	not policy.allow with input as inp
}

# --- Autonomous writes -----------------------------------------------------

test_low_risk_reversible_write_allowed_at_level_3 if {
	policy.allow with input as healer_write
	not policy.require_hitl with input as healer_write
}

test_write_escalates_when_task_level_too_low if {
	inp := object.union(healer_write, {"task": {"id": "task-002", "autonomy_level": 2}})
	not policy.allow with input as inp
	policy.require_hitl with input as inp
	"autonomy_level_insufficient" in policy.reasons with input as inp
}

test_kill_switch_stops_autonomous_writes if {
	not policy.allow with input as healer_write with data.aegislake.controls.kill_switch as true
	policy.require_hitl with input as healer_write with data.aegislake.controls.kill_switch as true
}

test_kill_switch_does_not_block_reads if {
	policy.allow with input as analyst_read with data.aegislake.controls.kill_switch as true
}

test_healer_cannot_publish_its_own_fix if {
	inp := object.union(healer_write, {"tool": {"name": "promote_wap_branch"}})
	not policy.allow with input as inp
	not policy.require_hitl with input as inp
}

test_publish_allowed_when_proposer_differs if {
	policy.allow with input as publisher_write
}

test_publish_escalates_when_proposer_is_the_publisher if {
	inp := object.union(publisher_write, {"request": {
		"estimated_tokens": 500,
		"proposer_spiffe_id": "spiffe://example.internal/ns/platform/sa/publisher",
	}})
	not policy.allow with input as inp
	policy.require_hitl with input as inp
	"second_party_required" in policy.reasons with input as inp
}

test_publish_escalates_when_proposer_missing if {
	inp := object.union(object.remove(publisher_write, ["request"]), {"request": {"estimated_tokens": 500}})
	not policy.allow with input as inp
	policy.require_hitl with input as inp
}

test_high_risk_write_always_escalates if {
	inp := object.union(publisher_write, {"tool": {"name": "promote_breaking_schema"}})
	not policy.allow with input as inp
	policy.require_hitl with input as inp
}

test_tool_with_no_allowed_roles_is_denied if {
	inp := object.union(publisher_write, {"tool": {"name": "purge_audit_partition"}})
	not policy.allow with input as inp
	not policy.require_hitl with input as inp
}
