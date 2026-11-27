"""
AegisLake MCP tool gateway: policy enforcement point (reference implementation)
-------------------------------------------------------------------------------
Shows how a gateway decides whether an agent may call a tool (ADR-007, ADR-009):

1. The caller's identity arrives as three parts: subject (who the call is for),
   actor (which agent workload is calling) and task (the unit of work and its
   autonomy level). In production these come from validated tokens. Here they
   are passed in as a CallContext.
2. The gateway builds the policy input itself. Facts about the tool come from the
   reviewed tool registry and facts about the data come from the catalog. Nothing
   the agent writes in its tool arguments is treated as a statement about risk or
   sensitivity.
3. The decision is made by Open Policy Agent using
   platform/policies/opa/mcp_agent_guardrails.rego. If OPA cannot be reached, the
   call is denied.
4. Every decision is appended to an audit log.

What this file is not: it does not speak the MCP wire protocol, and the tool
handlers return sample data. It demonstrates the enforcement logic only.

Run (after `docker compose -f docker-compose.local.yml up -d opa`):
    python3 agents/mcp-servers/lakehouse_mcp_server.py
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

OPA_DECISION_URL = os.environ.get(
    "OPA_DECISION_URL", "http://localhost:8181/v1/data/aegislake/mcp/decision"
)


@dataclass(frozen=True)
class Subject:
    """The person, or accountable system principal, the call is made for."""

    id: str
    clearance: str  # public | internal | confidential | restricted


@dataclass(frozen=True)
class Actor:
    """The agent workload making the call."""

    spiffe_id: str
    role: str


@dataclass(frozen=True)
class Task:
    """The unit of work this call belongs to."""

    id: str
    autonomy_level: int  # 0..3, see ADR-009


@dataclass(frozen=True)
class CallContext:
    subject: Subject
    actor: Actor
    task: Task


@dataclass(frozen=True)
class ToolSpec:
    """How the gateway handles one tool. Risk metadata lives in the OPA registry."""

    handler: Callable[[Dict[str, Any]], Dict[str, Any]]
    resource_arg: Optional[str] = None  # argument that names the target asset
    change_arg: Optional[str] = None  # argument that names a prepared change


class OPAClient:
    """Asks OPA for a decision. Any failure is a deny."""

    def __init__(self, url: str = OPA_DECISION_URL, timeout_seconds: float = 2.0) -> None:
        self.url = url
        self.timeout_seconds = timeout_seconds

    def decide(self, policy_input: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps({"input": policy_input}).encode("utf-8")
        request = urllib.request.Request(
            self.url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                result = json.loads(response.read().decode("utf-8")).get("result")
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as error:
            return _deny(f"policy_engine_unavailable: {error}")
        if not isinstance(result, dict) or "allow" not in result:
            return _deny("policy_engine_returned_no_decision")
        return {
            "allow": result.get("allow") is True,
            "require_hitl": result.get("require_hitl") is True,
            "reasons": sorted(result.get("reasons", [])),
        }


def _deny(reason: str) -> Dict[str, Any]:
    return {"allow": False, "require_hitl": False, "reasons": [reason]}


class AegisLakeMCPServer:
    """Tool gateway: builds the policy input, asks OPA, audits, then runs the tool."""

    def __init__(self, opa: Optional[OPAClient] = None) -> None:
        self.opa = opa or OPAClient()
        self.audit_log: List[Dict[str, Any]] = []
        # Who prepared each pending change. In production this is the change record
        # store written when a branch or pull request is created.
        self.change_records: Dict[str, str] = {}
        self.tools: Dict[str, ToolSpec] = {
            "query_semantic_kpi": ToolSpec(self._query_semantic_kpi, resource_arg="dataset"),
            "lookup_lineage": ToolSpec(self._lookup_lineage),
            "quarantine_invalid_records": ToolSpec(
                self._quarantine_invalid_records, resource_arg="dataset"
            ),
            "promote_wap_branch": ToolSpec(
                self._promote_wap_branch, resource_arg="dataset", change_arg="change_id"
            ),
        }

    def record_change(self, change_id: str, prepared_by_spiffe_id: str) -> None:
        self.change_records[change_id] = prepared_by_spiffe_id

    def invoke_tool(
        self, ctx: CallContext, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        spec = self.tools.get(tool_name)
        policy_input = self._build_policy_input(ctx, tool_name, spec, arguments)
        decision = self.opa.decide(policy_input)

        self.audit_log.append(
            {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "subject": ctx.subject.id,
                "actor": ctx.actor.spiffe_id,
                "task": ctx.task.id,
                "tool": tool_name,
                "resource": policy_input["resource"]["name"],
                "decision": decision,
            }
        )
        audit_id = len(self.audit_log)

        if not decision["allow"]:
            status = "HITL_REQUIRED" if decision["require_hitl"] else "DENIED"
            return {"status": status, "reasons": decision["reasons"], "audit_id": audit_id}
        if spec is None:
            # The registry allows a tool this gateway has no handler for.
            return {"status": "DENIED", "reasons": ["no_handler_for_tool"], "audit_id": audit_id}
        return {"status": "OK", "result": spec.handler(arguments), "audit_id": audit_id}

    def _build_policy_input(
        self,
        ctx: CallContext,
        tool_name: str,
        spec: Optional[ToolSpec],
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Everything here is set by the gateway. Agent arguments only select *which*
        asset or change is meant. The policy looks up what that asset or change is."""
        resource_name = ""
        change_id = ""
        if spec is not None:
            if spec.resource_arg:
                resource_name = str(arguments.get(spec.resource_arg, ""))
            if spec.change_arg:
                change_id = str(arguments.get(spec.change_arg, ""))

        request: Dict[str, Any] = {"estimated_tokens": self._estimate_tokens(arguments)}
        proposer = self.change_records.get(change_id)
        if proposer:
            request["proposer_spiffe_id"] = proposer

        return {
            "subject": {"id": ctx.subject.id, "clearance": ctx.subject.clearance},
            "actor": {"spiffe_id": ctx.actor.spiffe_id, "role": ctx.actor.role},
            "task": {"id": ctx.task.id, "autonomy_level": ctx.task.autonomy_level},
            "tool": {"name": tool_name},
            "resource": {"name": resource_name},
            "request": request,
        }

    @staticmethod
    def _estimate_tokens(arguments: Dict[str, Any]) -> int:
        """Gateway-side estimate: a base cost plus roughly four characters per token."""
        return 500 + len(json.dumps(arguments, default=str)) // 4

    # --- Tool handlers (sample data) -----------------------------------------

    def _query_semantic_kpi(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "metric": args.get("metric_name", "monthly_claim_approval_rate"),
            "source": "semantic-layer",
            "certified": True,
            "value": 0.942,
            "citation": f"{args.get('dataset', '')}@snapshot_884210",
        }

    def _lookup_lineage(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "dataset": args.get("dataset", "gold.claims.claim_risk_features_daily"),
            "upstream": ["kafka://ent.claims.submitted.v1", "silver.claims.conformed_claims"],
            "downstream": ["semantic://claims_kpis", "features://fraud_risk_features"],
        }

    def _quarantine_invalid_records(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "dataset": args.get("dataset"),
            "branch": args.get("branch"),
            "quarantined_rows": 42,
            "main_changed": False,
        }

    def _promote_wap_branch(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"dataset": args.get("dataset"), "change_id": args.get("change_id"), "published": True}


def _demo() -> None:
    server = AegisLakeMCPServer()

    analyst = CallContext(
        Subject("user-1", "internal"),
        Actor("spiffe://example.internal/ns/agents/sa/bi-copilot", "data_analyst_agent"),
        Task("task-001", autonomy_level=1),
    )
    healer = CallContext(
        Subject("svc-self-heal", "confidential"),
        Actor("spiffe://example.internal/ns/platform/sa/self-heal", "platform_self_healing_agent"),
        Task("task-002", autonomy_level=3),
    )
    publisher = CallContext(
        Subject("svc-publisher", "confidential"),
        Actor("spiffe://example.internal/ns/platform/sa/publisher", "platform_publisher_agent"),
        Task("task-003", autonomy_level=3),
    )
    confidential_table = "gold.claims.claim_risk_features_daily"
    server.record_change("chg-7", prepared_by_spiffe_id=healer.actor.spiffe_id)

    calls = [
        ("Analyst reads an internal KPI", analyst, "query_semantic_kpi",
         {"dataset": "gold.claims.claim_volume_by_region", "metric_name": "claims_per_region"}),
        ("Analyst reads a confidential table without clearance", analyst, "query_semantic_kpi",
         {"dataset": confidential_table, "metric_name": "avg_claim_amount"}),
        ("Analyst claims the data is harmless (ignored by the gateway)", analyst, "query_semantic_kpi",
         {"dataset": confidential_table, "contains_pii": False, "blast_radius": "low"}),
        ("Healer quarantines rows on an audit branch", healer, "quarantine_invalid_records",
         {"dataset": confidential_table, "branch": "wap_20261128_01"}),
        ("Healer tries to publish its own fix", healer, "promote_wap_branch",
         {"dataset": confidential_table, "change_id": "chg-7"}),
        ("Publisher publishes the healer's fix", publisher, "promote_wap_branch",
         {"dataset": confidential_table, "change_id": "chg-7"}),
        ("Publisher publishes a change with no recorded preparer", publisher, "promote_wap_branch",
         {"dataset": confidential_table, "change_id": "chg-unknown"}),
        ("Unknown tool", analyst, "drop_everything", {}),
    ]
    for label, ctx, tool, arguments in calls:
        outcome = server.invoke_tool(ctx, tool, arguments)
        detail = outcome.get("reasons") or ""
        print(f"{outcome['status']:<14} {label} {detail}")


if __name__ == "__main__":
    _demo()
