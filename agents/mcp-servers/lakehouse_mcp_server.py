"""
AegisLake Governed MCP Server (Reference Implementation)
--------------------------------------------------------
Exposes enterprise Lakehouse, Semantic Layer, and Metadata capabilities as
Zero-Trust Model Context Protocol (MCP) tools guarded by OPA policy checks
and immutable audit logging.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List
import json


@dataclass
class AgentContext:
    agent_id: str
    agent_role: str
    agent_clearance: str  # e.g., "standard" | "pii_authorized"
    spiffe_id: str


class OPAPolicyClient:
    """Evaluates tool invocations against platform/policies/opa/mcp_agent_guardrails.rego."""

    READ_ONLY_TOOLS = {
        "query_semantic_kpi",
        "lookup_datahub_lineage",
        "inspect_iceberg_wap_branch",
        "search_hybrid_knowledge_base",
    }
    REMEDIATION_TOOLS = {
        "quarantine_invalid_records",
        "trigger_iceberg_compaction",
        "open_dbt_evolution_pr",
        "promote_wap_branch",
    }

    def authorize(
        self,
        ctx: AgentContext,
        tool: str,
        contains_pii: bool = False,
        mutation: bool = False,
        blast_radius: str = "low",
    ) -> Dict[str, Any]:
        if tool in self.READ_ONLY_TOOLS and not mutation:
            if contains_pii and ctx.agent_clearance != "pii_authorized":
                return {"allow": False, "require_hitl": False, "reason": "PII clearance required"}
            return {"allow": True, "require_hitl": False, "reason": "Read-only tool authorized"}

        if (
            ctx.agent_role == "platform_self_healing_agent"
            and tool in self.REMEDIATION_TOOLS
            and blast_radius == "low"
        ):
            return {"allow": True, "require_hitl": False, "reason": "Low-risk Self-Heal authorized"}

        return {"allow": False, "require_hitl": True, "reason": "Escalated to HITL approval board"}


class AegisLakeMCPServer:
    """Governed MCP Tool Registry for Semantic KPIs, Lineage, and Iceberg Operations."""

    def __init__(self) -> None:
        self.opa = OPAPolicyClient()
        self.audit_log: List[Dict[str, Any]] = []

    def invoke_tool(self, ctx: AgentContext, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        mutation = tool_name not in OPAPolicyClient.READ_ONLY_TOOLS
        contains_pii = bool(arguments.get("contains_pii", False))
        blast_radius = str(arguments.get("blast_radius", "low"))

        decision = self.opa.authorize(ctx, tool_name, contains_pii, mutation, blast_radius)
        audit_entry = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "spiffe_id": ctx.spiffe_id,
            "agent_role": ctx.agent_role,
            "tool": tool_name,
            "decision": decision,
        }
        self.audit_log.append(audit_entry)

        if not decision["allow"]:
            return {
                "status": "HITL_REQUIRED" if decision["require_hitl"] else "DENIED",
                "reason": decision["reason"],
                "audit_id": len(self.audit_log),
            }

        handler = getattr(self, f"_tool_{tool_name}", None)
        if not handler:
            return {"status": "ERROR", "reason": f"Unknown tool: {tool_name}"}

        result = handler(arguments)
        return {"status": "OK", "result": result, "audit_id": len(self.audit_log)}

    def _tool_query_semantic_kpi(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "metric": args.get("metric_name", "monthly_claim_approval_rate"),
            "semantic_layer": "cube-metricflow",
            "certified": True,
            "value": 0.942,
            "citation": "gold.claims.claim_risk_features_daily@snapshot_884210",
        }

    def _tool_lookup_datahub_lineage(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "dataset": args.get("dataset", "gold.claims.claim_risk_features_daily"),
            "upstream": ["kafka://ent.claims.submitted.v1", "silver.claims.conformed_claims"],
            "downstream": ["cube://claims_kpis", "feast://fraud_risk_features"],
        }


if __name__ == "__main__":
    server = AegisLakeMCPServer()
    analyst = AgentContext(
        agent_id="copilot-01",
        agent_role="data_analyst_agent",
        agent_clearance="standard",
        spiffe_id="spiffe://aegislake.internal/ns/agents/sa/bi-copilot",
    )
    print(json.dumps(server.invoke_tool(analyst, "query_semantic_kpi", {"metric_name": "sla_compliance"}), indent=2))
    print(json.dumps(server.invoke_tool(analyst, "promote_breaking_schema", {"blast_radius": "high"}), indent=2))
