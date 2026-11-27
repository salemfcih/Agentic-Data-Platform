# ADR-003: Scope LakeFS to Unstructured AI Corpora and Use Native Iceberg WAP for Structured Tables

- **Status**: Accepted
- **Date**: 2026-11-23

## Context
Wrapping Apache Iceberg tables inside LakeFS branches introduces dual-versioning hazards, requires LakeFS Enterprise licensing for native Iceberg integration, and conflicts with Iceberg's native `Refs` branching semantics.

## Decision
1. Use **Apache Iceberg Native Write-Audit-Publish (WAP) Branching** for all Bronze/Silver/Gold tabular CI/CD and Self-Healing quarantine loops.
2. Scope **LakeFS** strictly to **unstructured multimodal AI datasets** (PDFs, medical/claims documents, audio, video, fine-tuning corpora, and model checkpoints) where Git-like atomic cross-file commits are indispensable.

## Alternatives Considered
| Option | Assessment |
| :--- | :--- |
| LakeFS for tables and files | One tool, but two versioning systems would then manage the same Iceberg tables. |
| Project Nessie branches for tables | Catalog-level branching across tables. Would replace Polaris as the catalog, which ADR-002 keeps. |
| No branching: staging tables and swap | Works everywhere, but has no atomic publish and no branch-level audit. |
| DVC for unstructured corpora | Fits small teams. Weaker for large shared object stores and access control. |
| **Iceberg WAP for tables, LakeFS for corpora** | **Chosen.** |

## Consequences
- **Positive**: One versioning mechanism per data type, so table references are never managed by two systems. Tables and corpora are both reproducible by reference without copying data.
- **Negative**: Publishing through a branch on continuously written streaming tables needs a micro-batch publish design. Branch write support must be verified for each engine and version. Two versioning tools must be operated.
