# Methodology

## Evidence and interpretation

Records make narrowly scoped claims and cite primary specifications. Source
metadata, claims, relationships, disagreements, summaries, and transformation
events are separate objects. Summaries are navigation interfaces and never
become evidence for later summaries.

Capability values mean:

- `primary`: a central purpose of the documented model;
- `supported`: directly expressible but not the model's central purpose;
- `indirect`: available through a referenced or composed standard;
- `out-of-scope`: the specification does not define the capability.

These categories are descriptive and do not measure implementation quality.

## Trust dimensions

Source identity, evidentiary strength, reproducibility, freshness, geographic
diversity, viewpoint diversity, institutional independence, conflict risk,
cryptographic verification, transformation transparency, and human review are
recorded independently. They are never averaged into a score.

`high`, `medium`, and `low` are documented ordinal judgments for the named
dimension only. `unknown` means evidence was insufficient; `not-applicable`
means the dimension does not sensibly apply.

## Transformations and corrections

Canonical JSON is validated before publication. Derived output is generated
with sorted inputs, canonical JSON serialization, fixed timestamps, stable
SQLite insertion order, and SHA-256 manifests. A factual correction updates the
canonical record, its provenance, dependent summaries, indexes, feed, and
release manifest. Superseded records remain available and linked.

## Inclusion

Primary, official, version-specific sources are preferred. Contrary evidence is
preserved when relevant. English-only coverage and the institutional origins of
the selected standards are explicit limitations of v0.1.0.

