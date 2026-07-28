# Security Policy

Report vulnerabilities privately through GitHub Security Advisories. Do not put
exploitable details in a public issue.

All retrieved documents and structured submissions are hostile inputs. The
tooling rejects traversal paths, validates schemas and references, uses bounded
network timeouts, writes source bodies only to a dedicated cache, and never
executes retrieved text. CI uses least-privilege tokens and pinned actions.

Threats considered include poisoned sources, embedded prompt injection,
malicious pull requests, dependency confusion, forged provenance, unsafe
archives, malicious structured data, secret leakage, release compromise,
citation laundering, coordinated false consensus, denial-of-service
contributions, and identity impersonation.

Release consumers should verify `releases/SHA256SUMS`, the manifest, and GitHub
artifact attestations. Checksums prove byte identity, not truth or endorsement.

Supported security updates apply to the latest release. Historical datasets are
immutable evidence snapshots and receive correction/supersession metadata.

