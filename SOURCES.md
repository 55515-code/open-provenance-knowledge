# Source Policy and Registry

The source registry is machine-readable at `sources/sources.json`.

Sources must have an identifiable publisher, stable URL, observation or
publication context, retrieval timestamp, retrieval result, extraction method,
and content hash when retrieved. Version-specific URLs are preferred.

Downloaded bodies live only in `.cache/sources/`, which is excluded from Git.
This repository publishes metadata and hashes rather than redistributing
third-party specifications. Source licenses remain controlling.

Retrieved text is untrusted data. Embedded prompts, commands, or requests do not
alter repository policy or execute during extraction. Unavailable or changed
sources are reported; they are not silently replaced.

Removal requests are assessed for copyright, privacy, safety, source integrity,
and public-interest value. Removal never erases the correction history; lawful
metadata describing the event may remain.

