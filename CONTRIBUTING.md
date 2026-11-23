# Contributing to AegisLake

We welcome architecture improvements, reference implementations, new ADRs, OPA policies, and connector blueprints.

## How to Propose an Architectural Change
1. **Open an Architecture Decision Record (ADR)** under `docs/adr/ADR-XXX-short-title.md` following the MADR format (Context, Decision, Alternatives Considered, Consequences).
2. **Keep Vendor Neutrality**: Every component must have an open-source sovereign reference option and an optional managed cloud mapping in `docs/architecture/05-hybrid-sovereign-vs-cloud-mapping.md`.
3. **Zero Proprietary Data**: Never commit organization-specific credentials, hostnames, internal system names, or confidential metrics.
4. **Validate Policies & Contracts**: Ensure all `.rego` policies, ODCS YAML contracts, and AsyncAPI specs pass schema validation before opening a Pull Request.
