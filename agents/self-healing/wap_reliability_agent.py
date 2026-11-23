"""
AegisLake Self-Healing Data Reliability Agent (Reference State Machine)
-----------------------------------------------------------------------
Demonstrates the closed-loop Write-Audit-Publish (WAP) pattern on Apache Iceberg:
1. Sense contract check results on an isolated WAP branch.
2. Classify failure severity (row-level defect vs. breaking schema change).
3. Enforce OPA policy gate: autonomously quarantine malformed rows OR open a HITL PR.
4. Keep the Gold `main` branch 100% uncorrupted at all times.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import json


@dataclass
class ContractCheckResult:
    table: str
    wap_branch: str
    total_rows: int
    malformed_rows: int
    breaking_schema_drift: bool
    drift_details: List[str]


def run_self_healing_loop(check: ContractCheckResult) -> Dict[str, Any]:
    error_ratio = check.malformed_rows / max(check.total_rows, 1)

    if check.malformed_rows == 0 and not check.breaking_schema_drift:
        return {
            "table": check.table,
            "wap_branch": check.wap_branch,
            "action": "FAST_FORWARD_MERGE_TO_MAIN",
            "hitl_required": False,
            "summary": "All ODCS v3 & Soda v4 gates passed; branch promoted cleanly.",
        }

    if check.breaking_schema_drift:
        return {
            "table": check.table,
            "wap_branch": check.wap_branch,
            "action": "BLOCK_MERGE_AND_OPEN_GITOPS_PR",
            "hitl_required": True,
            "drift_details": check.drift_details,
            "summary": (
                "Breaking schema change detected. Gold `main` protected. "
                "Draft SQLMesh/dbt migration PR + AsyncAPI diff sent to Domain Steward."
            ),
        }

    if error_ratio <= 0.02:
        return {
            "table": check.table,
            "wap_branch": check.wap_branch,
            "action": "AUTONOMOUS_QUARANTINE_AND_PROMOTE_CLEAN",
            "hitl_required": False,
            "clean_rows_promoted": check.total_rows - check.malformed_rows,
            "quarantined_rows": check.malformed_rows,
            "quarantine_table": f"{check.table}_quarantine",
            "summary": (
                f"Isolated {check.malformed_rows} malformed rows ({error_ratio:.2%}) to quarantine; "
                "promoted verified records to `main` and scheduled Temporal DLQ replay."
            ),
        }

    return {
        "table": check.table,
        "wap_branch": check.wap_branch,
        "action": "HALT_PIPELINE_AND_PAGE_STEWARD",
        "hitl_required": True,
        "error_ratio": round(error_ratio, 4),
        "summary": "Defect ratio exceeded autonomous threshold (>2%). Pipeline paused on WAP branch.",
    }


if __name__ == "__main__":
    sample_events = [
        ContractCheckResult("gold.claims.claim_risk_features_daily", "wap_20261123_01", 100000, 0, False, []),
        ContractCheckResult("gold.claims.claim_risk_features_daily", "wap_20261123_02", 100000, 42, False, []),
        ContractCheckResult(
            "gold.claims.claim_risk_features_daily",
            "wap_20261123_03",
            100000,
            0,
            True,
            ["Column `claim_amount_sar` changed from DECIMAL(18,2) to STRING"],
        ),
    ]
    for ev in sample_events:
        print(json.dumps(run_self_healing_loop(ev), indent=2))
