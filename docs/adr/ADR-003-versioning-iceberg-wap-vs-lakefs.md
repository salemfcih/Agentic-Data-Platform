# ADR-003: Scope LakeFS to Unstructured AI Corpora and Use Native Iceberg WAP for Structured Tables

- **Status**: Accepted
- **Date**: 2026-11-23

## Context
Wrapping Apache Iceberg tables inside LakeFS branches introduces dual-versioning hazards, requires LakeFS Enterprise licensing for native Iceberg integration, and conflicts with Iceberg's native `Refs` branching semantics.

## Decision
1. Use **Apache Iceberg Native Write-Audit-Publish (WAP) Branching** for all Bronze/Silver/Gold tabular CI/CD and Self-Healing quarantine loops.
2. Scope **LakeFS** strictly to **unstructured multimodal AI datasets** (PDFs, medical/claims documents, audio, video, fine-tuning corpora, and model checkpoints) where Git-like atomic cross-file commits are indispensable.

## Consequences
- **Positive**: Zero branching metadata corruption on Iceberg tables; full zero-copy reproducibility across both structured tables and unstructured AI corpora.
