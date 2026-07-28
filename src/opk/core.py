from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_VERSION = "1.0.0"
RELEASE = "0.1.0"
BASE_URL = "https://55515-code.github.io/open-provenance-knowledge/"
SOURCE_CUTOFF = "2026-07-28"
DEFAULT_EPOCH = 1785196800


class ValidationFailure(RuntimeError):
    """Raised when repository knowledge does not satisfy its public contract."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def content_hash(value: Any) -> str:
    clean = dict(value)
    clean.pop("content_hash", None)
    return "sha256:" + hashlib.sha256(canonical_bytes(clean)).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def load_inputs(root: Path) -> dict[str, list[dict[str, Any]]]:
    records = [load_json(path) for path in sorted((root / "records").glob("*.json"))]
    summaries = [load_json(path) for path in sorted((root / "summaries").glob("*.json"))]
    return {
        "records": [{**item, "content_hash": content_hash(item)} for item in records],
        "sources": load_json(root / "sources/sources.json"),
        "relationships": load_json(root / "relationships/interoperability.json"),
        "summaries": [{**item, "content_hash": content_hash(item)} for item in summaries],
        "provenance": [load_json(path) for path in sorted((root / "provenance").glob("*.json"))],
        "upstream": [load_json(path) for path in sorted((root / "upstream").glob("*.json"))],
        "downstream": load_json(root / "downstream/consumers.json"),
    }


def _validate_items(root: Path, items: list[dict[str, Any]], schema_name: str) -> list[str]:
    schema = load_json(root / f"schemas/{schema_name}.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for item in items:
        for error in sorted(validator.iter_errors(item), key=lambda e: list(e.path)):
            location = ".".join(str(part) for part in error.path) or "<root>"
            errors.append(f"{schema_name} {item.get('id', '<unknown>')} {location}: {error.message}")
    return errors


def validate(root: Path) -> dict[str, list[dict[str, Any]]]:
    data = load_inputs(root)
    schemas = {
        "records": "record",
        "sources": "source",
        "relationships": "relationship",
        "summaries": "summary",
        "provenance": "provenance",
        "upstream": "upstream-mapping",
        "downstream": "downstream-consumer",
    }
    errors: list[str] = []
    for key, schema in schemas.items():
        errors.extend(_validate_items(root, data[key], schema))

    record_ids = {item["id"] for item in data["records"]}
    source_ids = {item["id"] for item in data["sources"]}
    summary_ids = {item["id"] for item in data["summaries"]}
    all_artifact_ids = record_ids | source_ids | summary_ids

    def require(values: list[str], known: set[str], owner: str, field: str) -> None:
        for value in values:
            if value not in known:
                errors.append(f"{owner} has unresolved {field}: {value}")

    for record in data["records"]:
        require(record["source_ids"], source_ids, record["id"], "source")
        require(record["conflicts"], record_ids, record["id"], "conflict")
        if record["superseded_by"]:
            require([record["superseded_by"]], record_ids, record["id"], "superseded_by")
        require(record["supersedes"], record_ids, record["id"], "supersedes")
    for source in data["sources"]:
        parsed = urllib.parse.urlparse(source["canonical_url"])
        if parsed.scheme not in {"https", "http"} or not parsed.netloc:
            errors.append(f"{source['id']} has malformed canonical_url")
        try:
            datetime.fromisoformat(source["retrieved_at"].replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"{source['id']} has malformed retrieved_at")
    for relationship in data["relationships"]:
        require([relationship["subject_id"], relationship["object_id"]], record_ids, relationship["id"], "record")
        require(relationship["source_ids"], source_ids, relationship["id"], "source")
    for summary in data["summaries"]:
        require(summary["record_ids"], record_ids, summary["id"], "record")
    for event in data["provenance"]:
        require(event["artifact_ids"], all_artifact_ids, event["id"], "artifact")
        require(event["inputs"], source_ids | record_ids, event["id"], "input")

    identifiers = [item["id"] for group in data.values() for item in group if "id" in item]
    duplicates = sorted({identifier for identifier in identifiers if identifiers.count(identifier) > 1})
    if duplicates:
        errors.append(f"duplicate identifiers: {', '.join(duplicates)}")
    if errors:
        raise ValidationFailure("\n".join(errors))
    return data


def generated_at(epoch: int) -> str:
    return datetime.fromtimestamp(epoch, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _topic_markdown(data: dict[str, list[dict[str, Any]]]) -> str:
    summary = data["summaries"][0]
    lines = [
        "# Open provenance standards interoperability",
        "",
        f"> {summary['one_sentence']}",
        "",
        "This comparison describes documented scope and capabilities. It is not a",
        "ranking, compliance certification, endorsement, or assertion of equivalence.",
        "",
        "## Capability crosswalk",
        "",
        "| Standard | Identity | Digest | Provenance | SBOM | Relationships | Signing | Serialization |",
        "|---|---|---|---|---|---|---|---|",
    ]
    keys = ["identity", "digest", "provenance", "sbom", "relationships", "signing", "serialization"]
    for record in sorted(data["records"], key=lambda item: item["title"]):
        values = " | ".join(record["capabilities"][key] for key in keys)
        lines.append(f"| [{record['title']}]({record['id']}) | {values} |")
    lines.extend(["", "## Evidence-scoped profiles", ""])
    sources = {item["id"]: item for item in data["sources"]}
    for record in sorted(data["records"], key=lambda item: item["title"]):
        lines.extend(
            [
                f"### {record['title']}",
                "",
                record["claim"],
                "",
                f"Canonical ID: `{record['id']}`  ",
                f"Verified: {record['verified_at']}  ",
                "Sources: "
                + ", ".join(
                    f"[{sources[source_id]['title']}]({sources[source_id]['canonical_url']})"
                    for source_id in record["source_ids"]
                ),
                "",
            ]
        )
    lines.extend(["## Composition and non-equivalence", ""])
    records = {item["id"]: item["title"] for item in data["records"]}
    for item in data["relationships"]:
        lines.append(
            f"- **{records[item['subject_id']]} {item['predicate']} "
            f"{records[item['object_id']]}:** {item['note']}"
        )
    lines.extend(
        [
            "",
            "## Disagreement and omissions",
            "",
            summary["disagreement"],
            "",
            "Known omissions:",
            "",
            *[f"- {item}" for item in summary["known_omissions"]],
            "",
        ]
    )
    return "\n".join(lines)


def _build_sqlite(path: Path, data: dict[str, list[dict[str, Any]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        PRAGMA page_size=4096;
        PRAGMA journal_mode=DELETE;
        CREATE TABLE schema_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE records (id TEXT PRIMARY KEY, title TEXT, status TEXT, json TEXT NOT NULL);
        CREATE TABLE sources (id TEXT PRIMARY KEY, title TEXT, canonical_url TEXT, json TEXT NOT NULL);
        CREATE TABLE relationships (id TEXT PRIMARY KEY, subject_id TEXT, predicate TEXT, object_id TEXT, status TEXT, json TEXT NOT NULL);
        CREATE TABLE conflicts (record_id TEXT, conflict_id TEXT, PRIMARY KEY(record_id, conflict_id));
        CREATE TABLE summaries (id TEXT PRIMARY KEY, json TEXT NOT NULL);
        CREATE TABLE provenance_events (id TEXT PRIMARY KEY, json TEXT NOT NULL);
        CREATE TABLE releases (version TEXT PRIMARY KEY, source_cutoff TEXT NOT NULL);
        """
    )
    connection.executemany(
        "INSERT INTO schema_metadata VALUES (?, ?)",
        [("schema_version", SCHEMA_VERSION), ("canonical_base", BASE_URL + "id/")],
    )
    for item in sorted(data["records"], key=lambda value: value["id"]):
        connection.execute(
            "INSERT INTO records VALUES (?, ?, ?, ?)",
            (item["id"], item["title"], item["status"], canonical_bytes(item).decode().strip()),
        )
        connection.executemany(
            "INSERT INTO conflicts VALUES (?, ?)",
            [(item["id"], conflict_id) for conflict_id in sorted(item["conflicts"])],
        )
    for item in sorted(data["sources"], key=lambda value: value["id"]):
        connection.execute(
            "INSERT INTO sources VALUES (?, ?, ?, ?)",
            (item["id"], item["title"], item["canonical_url"], canonical_bytes(item).decode().strip()),
        )
    for item in sorted(data["relationships"], key=lambda value: value["id"]):
        connection.execute(
            "INSERT INTO relationships VALUES (?, ?, ?, ?, ?, ?)",
            (
                item["id"],
                item["subject_id"],
                item["predicate"],
                item["object_id"],
                item["status"],
                canonical_bytes(item).decode().strip(),
            ),
        )
    for item in sorted(data["summaries"], key=lambda value: value["id"]):
        connection.execute(
            "INSERT INTO summaries VALUES (?, ?)", (item["id"], canonical_bytes(item).decode().strip())
        )
    for item in sorted(data["provenance"], key=lambda value: value["id"]):
        connection.execute(
            "INSERT INTO provenance_events VALUES (?, ?)",
            (item["id"], canonical_bytes(item).decode().strip()),
        )
    connection.execute("INSERT INTO releases VALUES (?, ?)", (RELEASE, SOURCE_CUTOFF))
    connection.commit()
    connection.execute("VACUUM")
    connection.close()


def _media_type(path: str) -> str:
    suffixes = {
        ".json": "application/json",
        ".jsonld": "application/ld+json",
        ".csv": "text/csv",
        ".sqlite": "application/vnd.sqlite3",
        ".atom": "application/atom+xml",
        ".xml": "application/xml",
        ".txt": "text/plain",
        ".md": "text/markdown",
    }
    return suffixes.get(Path(path).suffix, "application/octet-stream")


def build(root: Path, epoch: int = DEFAULT_EPOCH, revision: str = "source") -> dict[str, Any]:
    data = validate(root)
    stamp = generated_at(epoch)
    records_payload = {
        "schema_version": SCHEMA_VERSION,
        "release": RELEASE,
        "generated_at": stamp,
        "records": sorted(data["records"], key=lambda item: item["id"]),
    }
    write_json(root / "indexes/records.json", records_payload)
    graph = {
        "@context": {
            "@vocab": BASE_URL + "vocab/",
            "id": "@id",
            "type": "@type",
            "source": {"@id": "source", "@type": "@id"},
        },
        "@graph": [
            {
                "id": item["id"],
                "type": "StandardProfile",
                "name": item["title"],
                "claim": item["claim"],
                "source": item["source_ids"],
            }
            for item in sorted(data["records"], key=lambda value: value["id"])
        ]
        + sorted(data["relationships"], key=lambda value: value["id"]),
    }
    write_json(root / "indexes/knowledge.jsonld", graph)
    write_json(
        root / "indexes/topics.json",
        {
            "schema_version": SCHEMA_VERSION,
            "topics": [
                {
                    "id": BASE_URL + "id/topic/standards-interoperability",
                    "title": "Open provenance standards interoperability",
                    "record_ids": sorted(item["id"] for item in data["records"]),
                }
            ],
        },
    )
    write_json(
        root / "indexes/entities.json",
        {"schema_version": SCHEMA_VERSION, "entities": sorted(item["id"] for item in data["records"])},
    )
    write_json(
        root / "indexes/dependencies.json",
        {"schema_version": SCHEMA_VERSION, "relationships": data["relationships"]},
    )
    write_json(
        root / "indexes/changed-since.json",
        {
            "schema_version": SCHEMA_VERSION,
            "cutoff": SOURCE_CUTOFF,
            "changes": [{"id": item["id"], "updated_at": item["updated_at"]} for item in data["records"]],
        },
    )
    topic = _topic_markdown(data)
    (root / "topics").mkdir(exist_ok=True)
    (root / "topics/standards-interoperability.md").write_text(topic, encoding="utf-8", newline="\n")

    csv_path = root / "datasets/interoperability.csv"
    csv_path.parent.mkdir(exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        keys = ["identity", "digest", "provenance", "sbom", "relationships", "signing", "serialization"]
        writer.writerow(["schema_version", "id", "title", "version", *keys])
        for item in sorted(data["records"], key=lambda value: value["id"]):
            writer.writerow(
                [SCHEMA_VERSION, item["id"], item["title"], item["specification"]["version"]]
                + [item["capabilities"][key] for key in keys]
            )
    _build_sqlite(root / "datasets/open-provenance-knowledge.sqlite", data)

    feed_entries = "".join(
        f"<entry><id>{escape(item['id'])}</id><title>{escape(item['title'])}</title>"
        f"<updated>{item['updated_at']}</updated><link href=\"{escape(item['id'])}\"/></entry>"
        for item in sorted(data["records"], key=lambda value: value["id"])
    )
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<feed xmlns="http://www.w3.org/2005/Atom">'
        f"<id>{BASE_URL}feeds/updates.atom</id><title>Open Provenance Knowledge updates</title>"
        f"<updated>{stamp}</updated>{feed_entries}</feed>\n"
    )
    (root / "feeds").mkdir(exist_ok=True)
    (root / "feeds/updates.atom").write_text(feed, encoding="utf-8", newline="\n")

    paths = [
        "",
        "interoperability/",
        "indexes/records.json",
        "indexes/knowledge.jsonld",
        "datasets/interoperability.csv",
        "datasets/open-provenance-knowledge.sqlite",
        "feeds/updates.atom",
        "llms.txt",
        "llms-full.txt",
    ] + [item["id"].removeprefix(BASE_URL) for item in data["records"]]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join(f"  <url><loc>{escape(BASE_URL + path)}</loc></url>\n" for path in paths)
    sitemap += "</urlset>\n"
    (root / "sitemap.xml").write_text(sitemap, encoding="utf-8", newline="\n")
    (root / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8", newline="\n"
    )
    (root / "llms.txt").write_text(
        "# Open Provenance Knowledge\n"
        "> Evidence-backed interoperability records for open software provenance standards.\n\n"
        f"- [Records]({BASE_URL}indexes/records.json)\n"
        f"- [Knowledge graph]({BASE_URL}indexes/knowledge.jsonld)\n"
        f"- [Agent rules]({BASE_URL}AGENTS.md)\n"
        f"- [Updates]({BASE_URL}feeds/updates.atom)\n",
        encoding="utf-8",
        newline="\n",
    )
    (root / "llms-full.txt").write_text(
        (root / "llms.txt").read_text(encoding="utf-8")
        + "\n## Retrieval summary\n\n"
        + data["summaries"][0]["retrieval"]
        + "\n\n## Evidence rules\n\n"
        + (root / "AGENTS.md").read_text(encoding="utf-8"),
        encoding="utf-8",
        newline="\n",
    )
    public_copies = [
        "indexes/records.json",
        "indexes/knowledge.jsonld",
        "indexes/topics.json",
        "indexes/entities.json",
        "indexes/dependencies.json",
        "indexes/changed-since.json",
        "datasets/interoperability.csv",
        "datasets/open-provenance-knowledge.sqlite",
        "feeds/updates.atom",
        "robots.txt",
        "sitemap.xml",
        "llms.txt",
        "llms-full.txt",
        "AGENTS.md",
    ]
    for relative in public_copies:
        destination = root / "site-content" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / relative, destination)
    (root / "site-content/interoperability.md").write_text(topic, encoding="utf-8", newline="\n")
    sources_by_id = {item["id"]: item for item in data["sources"]}
    for record in data["records"]:
        identifier_path = record["id"].removeprefix(BASE_URL + "id/")
        source_links = "\n".join(
            f"- [{sources_by_id[source_id]['title']}]({sources_by_id[source_id]['canonical_url']})"
            for source_id in record["source_ids"]
        )
        identifier_page = (
            f"# {record['title']}\n\n"
            f"Canonical ID: `{record['id']}`\n\n"
            f"{record['claim']}\n\n"
            f"Status: `{record['status']}`  \n"
            f"Verified: `{record['verified_at']}`  \n"
            f"Content hash: `{record['content_hash']}`\n\n"
            f"## Primary sources\n\n{source_links}\n"
        )
        target = root / "site-content/id" / f"{identifier_path}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(identifier_page, encoding="utf-8", newline="\n")

    artifact_paths = [
        "indexes/records.json",
        "indexes/knowledge.jsonld",
        "indexes/topics.json",
        "indexes/entities.json",
        "indexes/dependencies.json",
        "indexes/changed-since.json",
        "datasets/interoperability.csv",
        "datasets/open-provenance-knowledge.sqlite",
        "feeds/updates.atom",
        "topics/standards-interoperability.md",
        "robots.txt",
        "sitemap.xml",
        "llms.txt",
        "llms-full.txt",
    ]
    artifacts = []
    for relative in artifact_paths:
        payload = (root / relative).read_bytes()
        artifacts.append(
            {
                "path": relative,
                "media_type": _media_type(relative),
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "release": RELEASE,
        "generated_at": stamp,
        "source_cutoff": SOURCE_CUTOFF,
        "record_count": len(data["records"]),
        "build_revision": revision,
        "artifacts": artifacts,
    }
    _validate_items(root, [manifest], "release")
    write_json(root / "releases/manifest.json", manifest)
    (root / "releases/SHA256SUMS").write_text(
        "".join(f"{item['sha256']}  {item['path']}\n" for item in artifacts),
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def verify_release(root: Path, manifest_path: Path) -> None:
    manifest = load_json(manifest_path)
    errors = _validate_items(root, [manifest], "release")
    base = root.resolve()
    for artifact in manifest["artifacts"]:
        candidate = (root / artifact["path"]).resolve()
        if base not in candidate.parents:
            errors.append(f"unsafe artifact path: {artifact['path']}")
            continue
        if not candidate.is_file():
            errors.append(f"missing artifact: {artifact['path']}")
            continue
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if digest != artifact["sha256"]:
            errors.append(f"hash mismatch: {artifact['path']}")
    if errors:
        raise ValidationFailure("\n".join(errors))


def fetch_sources(root: Path) -> None:
    cache = root / ".cache/sources"
    cache.mkdir(parents=True, exist_ok=True)
    metadata_path = cache / "http-metadata.json"
    metadata = load_json(metadata_path) if metadata_path.exists() else {}
    for source in load_inputs(root)["sources"]:
        request = urllib.request.Request(source["canonical_url"], headers={"User-Agent": "opk/0.1"})
        previous = metadata.get(source["id"], {})
        if previous.get("etag"):
            request.add_header("If-None-Match", previous["etag"])
        if previous.get("last_modified"):
            request.add_header("If-Modified-Since", previous["last_modified"])
        try:
            with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
                body = response.read()
                filename = hashlib.sha256(source["id"].encode()).hexdigest() + ".bin"
                (cache / filename).write_bytes(body)
                metadata[source["id"]] = {
                    "url": response.url,
                    "etag": response.headers.get("ETag"),
                    "last_modified": response.headers.get("Last-Modified"),
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "retrieved_at": generated_at(int(datetime.now(tz=UTC).timestamp())),
                }
        except urllib.error.HTTPError as error:
            if error.code != 304:
                raise
    write_json(metadata_path, metadata)


def freshness_failures(root: Path, max_age_days: int = 365) -> list[str]:
    now = datetime.now(tz=UTC)
    failures = []
    for source in load_inputs(root)["sources"]:
        retrieved = datetime.fromisoformat(source["retrieved_at"].replace("Z", "+00:00"))
        age = (now - retrieved).days
        if age > max_age_days:
            failures.append(f"{source['id']} is {age} days old")
    return failures
