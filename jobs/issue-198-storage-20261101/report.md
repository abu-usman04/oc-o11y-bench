# Issue #198 Phase 2 storage measurements

One metadata-only and one retained-text replay per historical completed Investigation, using the current schema, real Integration foreign keys, lease predicates, row locking, and one committed INSERT transaction per Tool Run. EXPLAIN ANALYZE BUFFERS WAL measures INSERT execution including foreign-key triggers. Separate queries verify committed row and text sizes.

Single local replay per treatment, metadata-only first, no statistical latency claim. INSERT timings exclude row-lock acquisition, network/encoding, commit fsync and extra WAL for COMMIT. pg_column_size reports datum sizes with PostgreSQL storage behavior; it excludes page/index/backup overhead. This is a storage measurement, not a new model evaluation or release gate.

The exact historical prepared texts are unchanged. No provider calls were made and no old attempt was edited.

| Case | Runs | Text bytes | Stored text bytes | Metadata row bytes | Retained row bytes | Metadata INSERT ms | Retained INSERT ms | Metadata WAL | Retained WAL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| promql-error-rate | 6 | 6467 | 5218 | 4101 | 9328 | 8.033 | 7.73 | 4857 | 9994 |
| logql-deployment-rollout-events | 1 | 1754 | 667 | 537 | 1204 | 3.647 | 4.137 | 648 | 1315 |
| find-slow-traces | 10 | 17722 | 8854 | 6901 | 15780 | 8.482 | 8.313 | 8011 | 17124 |
| service-degradation-rca | 14 | 55658 | 18134 | 8757 | 26920 | 8.597 | 11.114 | 10311 | 29578 |

The control-plane composed HTTP tests separately verify an ordinary detail response below 4096 bytes while retaining a 65536-byte UTF-8 observation. Only the explicit one-run endpoint retrieves the body; Viewer access is refused. The ordinary SQL projection contains no observation body or Integration join.

The model-content budget remains 16 KiB. The fixed complete-text ceiling remains 64 KiB; 30 maximal observations total 1.875 MiB before storage/WAL/backup overhead. These few local replays do not justify changing either budget.

Observations follow their owning Investigation's existing deployment retention practices. No new expiry worker or content index is introduced. Protect retained text and backups as sensitive operational data; known-credential sanitization is not arbitrary secret detection.

See measurements.json for schema/diff provenance and the exact old job names. Final release verification and the four-case model reevaluation remain pending.

The initial text-mode replay is preserved in initial-text-mode.json and initial-text-mode.md but excluded: Windows stdin newline translation changed stored bytes. The final replay used binary UTF-8 and its raw text totals exactly match all four saved captures. Neither replay called a model provider.

Phase 2 implementation commit: aac63ffc92f7eb081acbc9d9fd3646536595211b. Measurement provenance records the schema hash and the working-tree diff at replay time; the timings measure SQL INSERT execution, not an application binary or provider delivery.
