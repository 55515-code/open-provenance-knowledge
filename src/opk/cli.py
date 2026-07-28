from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .core import (
    DEFAULT_EPOCH,
    ValidationFailure,
    build,
    fetch_sources,
    freshness_failures,
    validate,
    verify_release,
)


def repository_root() -> Path:
    return Path.cwd()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="opk")
    subcommands = result.add_subparsers(dest="command", required=True)
    subcommands.add_parser("validate")
    subcommands.add_parser("fetch-sources")
    freshness = subcommands.add_parser("check-freshness")
    freshness.add_argument("--max-age-days", type=int, default=365)
    builder = subcommands.add_parser("build")
    builder.add_argument(
        "--source-date-epoch",
        type=int,
        default=int(os.environ.get("SOURCE_DATE_EPOCH", DEFAULT_EPOCH)),
    )
    verifier = subcommands.add_parser("verify-release")
    verifier.add_argument("manifest", type=Path)
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    root = repository_root()
    try:
        if arguments.command == "validate":
            data = validate(root)
            print(f"valid: {len(data['records'])} records, {len(data['sources'])} sources")
        elif arguments.command == "fetch-sources":
            fetch_sources(root)
            print("source cache refreshed")
        elif arguments.command == "check-freshness":
            failures = freshness_failures(root, arguments.max_age_days)
            if failures:
                raise ValidationFailure("\n".join(failures))
            print("all sources are within the freshness window")
        elif arguments.command == "build":
            revision = os.environ.get("OPK_BUILD_REVISION", "v0.1.0-canonical")
            manifest = build(root, arguments.source_date_epoch, revision)
            print(f"built {len(manifest['artifacts'])} artifacts")
        elif arguments.command == "verify-release":
            verify_release(root, arguments.manifest)
            print("release artifacts verified")
    except (ValidationFailure, OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
