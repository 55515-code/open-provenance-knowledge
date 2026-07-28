# Research Findings

Observed on 2026-07-28:

- SLSA 1.2 separates security assurance expectations from concrete attestation
  formats and recommends an in-toto-compatible provenance predicate.
- in-toto Attestation Framework 1.2 separates predicate, statement, envelope,
  and bundle concerns and publishes vetted predicates.
- SPDX 3.0.1 uses an RDF-based data model with JSON-LD and other
  serializations, spanning more than licensing alone.
- CycloneDX 1.7 is a modular BOM standard that includes components, services,
  dependencies, vulnerabilities, formulation, declarations, and citations.

The standards compose in useful ways but are not interchangeable. A common
mistake is to compare SLSA directly to an SBOM format as if both answer the same
question. Another is to infer lossless SPDX/CycloneDX conversion without a
versioned mapping and tests.

