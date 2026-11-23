package aegislake.mcp

import rego.v1

# Default deny — Zero-Trust baseline (NIST SP 800-207)
default allow := false
default require_hitl := false

# Allowed read-only tools for analytical & conversational agents
read_only_tools := {
    "query_semantic_kpi",
    "lookup_datahub_lineage",
    "inspect_iceberg_wap_branch",
    "search_hybrid_knowledge_base",
}

# Controlled write/remediation tools restricted to platform Self-X agents
platform_remediation_tools := {
    "quarantine_invalid_records",
    "trigger_iceberg_compaction",
    "open_dbt_evolution_pr",
    "promote_wap_branch",
}

# High-risk mutations always require Human-in-the-Loop (HITL) approval
high_risk_tools := {
    "promote_breaking_schema",
    "deploy_prod_model_override",
    "purge_audit_partition",
}

# Rule 1: Read-only access allowed when PII clearance matches payload sensitivity
allow if {
    input.tool in read_only_tools
    input.mutation == false
    pii_cleared(input)
    within_budget(input)
}

# Rule 2: Platform Self-X agents can run low-risk autonomous remediation
allow if {
    input.agent_role == "platform_self_healing_agent"
    input.tool in platform_remediation_tools
    input.blast_radius == "low"
    within_budget(input)
}

# Rule 3: Escalate high-risk or breaking mutations to HITL
require_hitl if {
    input.tool in high_risk_tools
}

require_hitl if {
    input.mutation == true
    input.blast_radius != "low"
}

pii_cleared(req) if {
    req.contains_pii == false
}

pii_cleared(req) if {
    req.contains_pii == true
    req.agent_clearance == "pii_authorized"
    req.masking_enforced == true
}

within_budget(req) if {
    object.get(req, "estimated_tokens", 0) <= 50000
}
