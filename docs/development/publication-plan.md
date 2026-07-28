# Publication Plan

Canonical JSON is reviewed and validated first. The build then generates human
pages, indexes, graph data, bulk datasets, feeds, discovery files, checksums,
and a release manifest. CI repeats the build with a fixed epoch and rejects
drift.

GitHub Pages hosts the documentation and static endpoints. Signed version tags
create downloadable release artifacts and GitHub build-provenance attestations.
Corrections update canonical inputs and dependent outputs in a later release;
superseded identifiers remain resolvable.

The upstream in-toto crosswalk remains a draft until independently reviewed. It
will never be mass-submitted or described as accepted before upstream records
confirm that status.

