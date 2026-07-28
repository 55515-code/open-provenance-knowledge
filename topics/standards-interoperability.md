# Open provenance standards interoperability

> SLSA expresses security expectations and provenance predicates, in-toto carries authenticated claims, and SPDX and CycloneDX represent overlapping but non-equivalent supply-chain inventories.

This comparison describes documented scope and capabilities. It is not a
ranking, compliance certification, endorsement, or assertion of equivalence.

## Capability crosswalk

| Standard | Identity | Digest | Provenance | SBOM | Relationships | Signing | Serialization |
|---|---|---|---|---|---|---|---|
| [CycloneDX 1.7](https://55515-code.github.io/open-provenance-knowledge/id/standard/cyclonedx/1.7) | primary | supported | supported | primary | primary | supported | primary |
| [SLSA 1.2](https://55515-code.github.io/open-provenance-knowledge/id/standard/slsa/1.2) | supported | primary | primary | out-of-scope | supported | indirect | supported |
| [SPDX 3.0.1](https://55515-code.github.io/open-provenance-knowledge/id/standard/spdx/3.0.1) | primary | supported | supported | primary | primary | supported | primary |
| [in-toto Attestation Framework 1.2](https://55515-code.github.io/open-provenance-knowledge/id/standard/in-toto-attestation/1.2) | primary | primary | supported | indirect | primary | primary | primary |

## Evidence-scoped profiles

### CycloneDX 1.7

CycloneDX 1.7 defines a modular bill-of-materials model for components, services, dependencies, vulnerabilities, formulation, declarations, and related supply-chain information.

Canonical ID: `https://55515-code.github.io/open-provenance-knowledge/id/standard/cyclonedx/1.7`  
Verified: 2026-07-28T00:00:00Z  
Sources: [CycloneDX specification overview 1.7](https://cyclonedx.org/specification/overview/)

### SLSA 1.2

SLSA 1.2 defines incrementally adoptable supply-chain security levels and recommended attestation formats; it is not an SBOM format.

Canonical ID: `https://55515-code.github.io/open-provenance-knowledge/id/standard/slsa/1.2`  
Verified: 2026-07-28T00:00:00Z  
Sources: [SLSA specification 1.2](https://slsa.dev/spec/v1.2/)

### SPDX 3.0.1

SPDX 3.0.1 defines an RDF-based model and serializations for software, licensing, security, build, and supply-chain information, including SBOM use cases.

Canonical ID: `https://55515-code.github.io/open-provenance-knowledge/id/standard/spdx/3.0.1`  
Verified: 2026-07-28T00:00:00Z  
Sources: [SPDX specification 3.0.1](https://spdx.github.io/spdx-spec/v3.0.1/)

### in-toto Attestation Framework 1.2

The in-toto Attestation Framework 1.2 defines statement, predicate, envelope, and bundle layers for authenticated metadata about software artifacts.

Canonical ID: `https://55515-code.github.io/open-provenance-knowledge/id/standard/in-toto-attestation/1.2`  
Verified: 2026-07-28T00:00:00Z  
Sources: [in-toto Attestation Framework specification 1.2.0](https://github.com/in-toto/attestation/tree/v1.2.0/spec)

## Composition and non-equivalence

- **SLSA 1.2 uses-envelope in-toto Attestation Framework 1.2:** SLSA's recommended provenance is expressed as a predicate within an in-toto Statement.
- **in-toto Attestation Framework 1.2 defines-predicate SPDX 3.0.1:** The in-toto predicate registry includes SPDX predicate forms; this does not make SPDX and in-toto equivalent.
- **in-toto Attestation Framework 1.2 defines-predicate CycloneDX 1.7:** CycloneDX recognizes a BOM predicate type usable in in-toto attestations.
- **SPDX 3.0.1 not-equivalent-to CycloneDX 1.7:** Both can represent SBOM information, but their models, scopes, and serializations are not interchangeable without a defined mapping.

## Disagreement and omissions

The repository does not assert a universal best standard or lossless translation between SPDX and CycloneDX. Tool support and mapping completeness require ecosystem-specific evidence.

Known omissions:

- Tool-by-tool implementation coverage
- Non-English primary documentation
- Loss analysis for concrete format converters
