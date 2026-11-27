"""
AegisLake Self-Healing Data Reliability Agent (reference state machine)
-----------------------------------------------------------------------
Demonstrates the write-audit-publish (WAP) pattern on Apache Iceberg with the
safety rules from ADR-009:

1. Read the contract check results for an isolated audit branch.
2. Classify the failure: clean, row-level defects, or a breaking schema change.
3. Decide what the agent may do itself. It may quarantine rows on the branch.
   It never publishes to main. Publication is requested from a separate
   publisher identity (proposer is not approver).
4. Respect the data contract. If the contract requires completeness, a branch
   with quarantined rows is held for a person instead of being published partial.

Main is never written by this agent.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

CONTRACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "data-contracts"
    / "customer_claims_gold.odcs.yaml"
)


@dataclass(frozen=True)
class ContractPolicy:
    """The parts of a data contract this agent acts on."""

    completeness_required: bool = True  # safe default when the contract is unreadable
    max_quarantine_ratio: float = 0.02


@dataclass(frozen=True)
class ContractCheckResult:
    table: str
    wap_branch: str
    total_rows: int
    malformed_rows: int
    breaking_schema_drift: bool
    drift_details: List[str]


def load_contract_policy(path: Path = CONTRACT_PATH) -> ContractPolicy:
    """Read completenessRequired from an ODCS contract's customProperties.

    Falls back to the conservative default if PyYAML is missing or the file
    cannot be read.
    """
    try:
        import yaml  # type: ignore

        contract = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return ContractPolicy()
    properties = {
        item.get("property"): item.get("value")
        for item in contract.get("customProperties", [])
        if isinstance(item, dict)
    }
    return ContractPolicy(completeness_required=properties.get("completenessRequired", True) is not False)


def run_self_healing_loop(check: ContractCheckResult, policy: ContractPolicy) -> Dict[str, Any]:
    base = {"table": check.table, "wap_branch": check.wap_branch}
    error_ratio = check.malformed_rows / max(check.total_rows, 1)

    if check.breaking_schema_drift:
        return {
            **base,
            "action": "BLOCK_PUBLISH_AND_OPEN_PULL_REQUEST",
            "hitl_required": True,
            "drift_details": check.drift_details,
            "summary": (
                "Breaking schema change detected. Main is unchanged. A draft migration "
                "pull request and the event schema diff were sent to the domain steward."
            ),
        }

    if check.malformed_rows == 0:
        return {
            **base,
            "action": "REQUEST_PUBLISH_BY_PUBLISHER",
            "hitl_required": False,
            "summary": "All contract checks passed. Publication requested from the publisher identity.",
        }

    if error_ratio > policy.max_quarantine_ratio:
        return {
            **base,
            "action": "HALT_PIPELINE_AND_PAGE_STEWARD",
            "hitl_required": True,
            "error_ratio": round(error_ratio, 4),
            "summary": (
                f"Defect ratio {error_ratio:.2%} is above the autonomous limit "
                f"({policy.max_quarantine_ratio:.0%}). Pipeline paused on the audit branch."
            ),
        }

    quarantine = {
        "quarantined_rows": check.malformed_rows,
        "quarantine_table": f"{check.table}_quarantine",
        "clean_rows_on_branch": check.total_rows - check.malformed_rows,
    }

    if policy.completeness_required:
        return {
            **base,
            **quarantine,
            "action": "QUARANTINE_ON_BRANCH_AND_HOLD_PUBLISH",
            "hitl_required": True,
            "summary": (
                f"Quarantined {check.malformed_rows} rows ({error_ratio:.2%}) on the audit branch. "
                "The contract requires complete data, so main is not updated until the rows "
                "are repaired and the reconciliation check passes, or a steward approves."
            ),
        }

    return {
        **base,
        **quarantine,
        "action": "QUARANTINE_ON_BRANCH_AND_REQUEST_PUBLISH",
        "hitl_required": False,
        "summary": (
            f"Quarantined {check.malformed_rows} rows ({error_ratio:.2%}) on the audit branch. "
            "The contract allows partial data, so publication of the clean rows was requested "
            "from the publisher identity. Replay of repaired rows is scheduled only for "
            "consumers declared idempotent."
        ),
    }


if __name__ == "__main__":
    table = "gold.claims.claim_risk_features_daily"
    contract_policy = load_contract_policy()
    partial_allowed = ContractPolicy(completeness_required=False)

    scenarios = [
        ("clean branch", ContractCheckResult(table, "wap_20261128_01", 100000, 0, False, []), contract_policy),
        ("42 bad rows, contract as written", ContractCheckResult(table, "wap_20261128_02", 100000, 42, False, []), contract_policy),
        ("42 bad rows, contract allowing partial data", ContractCheckResult(table, "wap_20261128_02", 100000, 42, False, []), partial_allowed),
        ("5% bad rows", ContractCheckResult(table, "wap_20261128_03", 100000, 5000, False, []), contract_policy),
        (
            "breaking schema change",
            ContractCheckResult(
                table,
                "wap_20261128_04",
                100000,
                0,
                True,
                ["Column `claim_amount` changed from DECIMAL(18,2) to STRING"],
            ),
            contract_policy,
        ),
    ]
    print(f"Contract policy in effect: {contract_policy}\n")
    for label, check, policy in scenarios:
        print(f"--- {label}")
        print(json.dumps(run_self_healing_loop(check, policy), indent=2))
