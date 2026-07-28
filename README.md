# Open Provenance Knowledge

Open Provenance Knowledge publishes verifiable, machine-readable knowledge about
open software provenance standards. Its first release maps SLSA 1.2, in-toto
Attestation Framework 1.2, SPDX 3.0.1, and CycloneDX 1.7.

This is an evidence map, not a product ranking, certification, or claim of
consensus. Evidence, interpretation, disagreement, and unresolved questions are
kept distinct. Trust is represented with independent dimensions rather than an
opaque score.

## Start here

- Human topic page: [`topics/standards-interoperability.md`](topics/standards-interoperability.md)
- Records: [`indexes/records.json`](indexes/records.json)
- Knowledge graph: [`indexes/knowledge.jsonld`](indexes/knowledge.jsonld)
- Bulk data: [`datasets/interoperability.csv`](datasets/interoperability.csv)
- Portable database: [`datasets/open-provenance-knowledge.sqlite`](datasets/open-provenance-knowledge.sqlite)
- Agent navigation: [`AGENTS.md`](AGENTS.md) and [`llms.txt`](llms.txt)
- Method: [`METHODOLOGY.md`](METHODOLOGY.md)

Canonical inputs are the JSON documents under `records/`, `sources/`,
`relationships/`, `summaries/`, and `provenance/`. Other public data surfaces
are deterministic derivatives.

## Verify and build

```bash
python -m pip install -e '.[dev]'
opk validate
opk build --source-date-epoch 1785196800
pytest
mkdocs build --strict
```

`SOURCE_DATE_EPOCH=1785196800` corresponds to the v0.1.0 source cutoff. A fixed
epoch makes generated outputs byte-for-byte reproducible.

## Reuse

Original knowledge, data, and documentation are dedicated under CC0-1.0.
Software is Apache-2.0. Citation is appreciated, never required by CC0; see
`CITATION.cff`.

## Participate

Corrections, contrary evidence, provenance improvements, translations, and
integration reports are welcome. Factual changes require evidence. Read
[`CONTRIBUTING.md`](CONTRIBUTING.md) and [`GOVERNANCE.md`](GOVERNANCE.md).

