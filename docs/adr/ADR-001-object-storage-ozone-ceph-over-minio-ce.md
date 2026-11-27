# ADR-001: Adopt Apache Ozone / Ceph RGW Over MinIO Community Edition for Sovereign Object Storage

- **Status**: Accepted
- **Date**: 2026-11-23
- **Deciders**: Chief Data Architecture Board

## Context
Baseline open-source lakehouse designs frequently specify MinIO Community Edition (CE) as the on-premises S3-compatible object store. In May 2025 MinIO removed administrative functionality from the community web console. In October 2025 it stopped publishing community binaries and container images, leaving source-only distribution. In December 2025 the project entered maintenance mode, and the repository was archived in February 2026 and again in April 2026. The vendor now directs users to its commercial AIStor product.

## Decision
Deprecate MinIO Community Edition from the target reference architecture. Standardize sovereign on-premises S3-compatible storage on **Apache Ozone** (for Cloudera/Hadoop-aligned estates) or **Ceph RGW** (for general OpenShift/Kubernetes estates via Rook-Ceph), with **Cloud Object Storage (GCS / AWS S3)** for cloud-native deployments.

## Alternatives Considered
| Option | Assessment |
| :--- | :--- |
| Stay on MinIO CE, built from source | The adopter owns all patching for a frozen codebase. Not acceptable for a core storage tier. |
| MinIO AIStor (commercial) | Technically the closest replacement. Makes the storage tier depend on one vendor's licence terms, which conflicts with the sovereign, open-source baseline of this reference. |
| Community forks of MinIO | Emerged after the archive. Maintenance and security response are not yet proven. Re-evaluate later. |
| SeaweedFS | Lightweight and used in the local sandbox. Needs a separate production evaluation before being recommended at scale. |
| **Apache Ozone or Ceph RGW** | **Chosen.** Both are mature, openly governed and widely deployed. |

## Consequences
- **Positive**: Removes the dependency on an unmaintained codebase and on a single vendor's licence; native alignment with Apache Iceberg, Cloudera CDP, and OpenShift storage operators.
- **Negative**: Higher initial operational tuning compared to legacy single-binary MinIO; mitigated via Kubernetes Operators (Rook-Ceph) and declarative GitOps runbooks.
