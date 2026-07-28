# Local Preparation Audit

## Boundary

`/home/ahron/codespace` is an existing, heavily modified orchestrator checkout
with unrelated projects nested beneath it. Open Provenance Knowledge is created
as an independent sibling Git repository. No orchestrator files are inputs or
publication artifacts.

## Minimum substrate

The only private substrate is a gitignored HTTP cache containing source bytes
and conditional-request metadata. It prevents repeated downloads and supports
hash comparison. Canonical source metadata and transformation history are
public.

Deterministic local operations replace repeated model tasks for validation,
hashing, cross-reference checks, indexes, Markdown, CSV, SQLite, feeds,
sitemaps, and release manifests. No private semantic index or summary store is
required.

## Gaps

The initial source set is English-only; archived URLs and cryptographic
signatures were not available for every source; implementation-level adoption
evidence remains out of scope. These gaps are published rather than hidden.

