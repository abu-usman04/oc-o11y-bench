# Publish the OpenCluster benchmark repository

Status: published and verified on 2026-10-29 at https://github.com/abu-usman04/oc-o11y-bench. Public visibility was verified anonymously; remote file hashes match the reviewed local snapshot. All 329 job files are tracked. Configured-key, publication-snapshot and full-history secret scans passed.

## Scope

Publish the existing benchmark repository as public abu-usman04/oc-o11y-bench. Describe it as an o11y-bench agent and evaluation harness for testing OpenCluster observability investigations. Preserve its source, history, all job attempts and the independent correctness audit. Do not publish the production repository or change Agent behavior.

## Steps

1. Verify the authenticated personal GitHub account and repository name. Inspect all existing job files and tracked history for credentials before any public push.
2. Remove jobs from .gitignore. Keep completed configuration, secrets, upstream checkouts, virtual environments, workspace caches and local IDE files excluded. Verify jobs become trackable and configuration remains ignored using existing Git commands; no application logic changes or new test framework are needed.
3. Update only the relevant README sections and add a short jobs index. Preserve unsuccessful attempts. Copy the small audit verification logs into jobs and make audit links portable; retain raw Tool observations and endpoint metadata.
4. Stage only the intended source, documentation and jobs. Scan the exact publication snapshot and full reachable history with the existing secret scanner, plus check configured credential values without printing them. Resolve real findings before proceeding. Reuse existing focused checks appropriate to this metadata-only change.
5. Create the public personal repository with the requested description, commit the publication changes, push the current branch and make it the default. Verify public visibility, remote commit identity and tracked job artifacts. Do not overwrite an existing repository or force-push.

## Plan review

This is publication of the existing benchmark and its records. The existing Agent and production release blockers remain documented; publishing results does not claim they are fixed. All actual results are small enough for ordinary Git. No new abstractions, dependencies, CI workflows, licenses or deployment are required. Publication is explicitly authorized, so no further approval is needed after the checks pass.
