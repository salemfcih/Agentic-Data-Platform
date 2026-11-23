# ADR-001: Adopt Apache Ozone / Ceph RGW Over MinIO Community Edition for Sovereign Object Storage

- **Status**: Accepted
- **Date**: 2026-11-23
- **Deciders**: Chief Data Architecture Board

## Context
Baseline open-source lakehouse designs frequently specify MinIO Community Edition (CE) as the on-premises S3-compatible object store. Between May 2025 and September 2026, MinIO removed administrative functionality from the OSS web console, moved CE to source-only distribution, archived the OSS GitHub repository, left multiple 2026 CVEs unpatched in CE, and disabled anonymous container image pulls in favor of commercial MinIO AIStor (which enforces license expiration into read-only/offline modes).

## Decision
Deprecate MinIO Community Edition from the target reference architecture. Standardize sovereign on-premises S3-compatible storage on **Apache Ozone** (for Cloudera/Hadoop-aligned estates) or **Ceph RGW** (for general OpenShift/Kubernetes estates via Rook-Ceph), with **Cloud Object Storage (GCS / AWS S3)** for cloud-native deployments.

## Consequences
- **Positive**: Eliminates critical CVE/supply-chain exposure and AGPL/commercial license lock-in; native alignment with Apache Iceberg, Cloudera CDP, and OpenShift storage operators.
- **Negative**: Higher initial operational tuning compared to legacy single-binary MinIO; mitigated via Kubernetes Operators (Rook-Ceph) and declarative GitOps runbooks.
