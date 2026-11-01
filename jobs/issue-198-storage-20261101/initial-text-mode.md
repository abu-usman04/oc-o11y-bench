This initial replay is INVALID for exact-observation measurements: Windows text-mode stdin changed embedded LF to CRLF. It is preserved for the audit trail and superseded by report.md and measurements.json.

# Issue #198 Phase 2 storage measurements

One metadata-only and one retained-text replay per historical completed Investigation, using the current schema, real Integration foreign keys, lease predicates, row locking, and one committed INSERT transaction per Tool Run. EXPLAIN ANALYZE BUFFERS WAL measures INSERT execution including foreign-key triggers. Separate queries verify committed row and text sizes.

Single local replay per treatment, metadata-only first, no statistical latency claim. INSERT timings exclude row-lock acquisition, network/encoding, commit fsync and extra WAL for COMMIT. pg_column_size reports datum sizes with PostgreSQL storage behavior; it excludes page/index/backup overhead. This is a storage measurement, not a new model evaluation or release gate.

The exact historical prepared texts are unchanged. No provider calls were made and no old attempt was edited.

| Case | Runs | Text bytes | Stored text bytes | Metadata row bytes | Retained row bytes | Metadata INSERT ms | Retained INSERT ms | Metadata WAL | Retained WAL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| promql-error-rate | 6 | 6491 | 5241 | 4101 | 9351 | 6.675 | 7.575 | 4857 | 10017 |
| logql-deployment-rollout-events | 1 | 1758 | 671 | 537 | 1208 | 3.734 | 3.62 | 648 | 1319 |
| find-slow-traces | 10 | 17763 | 8892 | 6901 | 15818 | 8.778 | 10.592 | 8011 | 17162 |
| service-degradation-rca | 14 | 55715 | 18192 | 8757 | 26978 | 9.165 | 12.841 | 10311 | 29636 |

The control-plane composed HTTP tests separately verify an ordinary detail response below 4096 bytes while retaining a 65536-byte UTF-8 observation. Only the explicit one-run endpoint retrieves the body; Viewer access is refused. The ordinary SQL projection contains no observation body or Integration join.

The model-content budget remains 16 KiB. The fixed complete-text ceiling remains 64 KiB; 30 maximal observations total 1.875 MiB before storage/WAL/backup overhead. These few local replays do not justify changing either budget.

Observations follow their owning Investigation's existing deployment retention practices. No new expiry worker or content index is introduced. Protect retained text and backups as sensitive operational data; known-credential sanitization is not arbitrary secret detection.

See measurements.json for schema/diff provenance and the exact old job names. Final release verification and the four-case model reevaluation remain pending.
