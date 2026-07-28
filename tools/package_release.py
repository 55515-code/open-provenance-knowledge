"""Create deterministic v0.1.0 release archives."""

from __future__ import annotations

import gzip
import tarfile
import zipfile
from pathlib import Path

EPOCH = 1785196800
ROOT = Path(__file__).parents[1]
DIST = ROOT / "dist"
FILES = [
    "indexes/records.json",
    "indexes/knowledge.jsonld",
    "datasets/interoperability.csv",
    "datasets/open-provenance-knowledge.sqlite",
    "feeds/updates.atom",
    "releases/manifest.json",
    "releases/SHA256SUMS",
]


def main() -> None:
    DIST.mkdir(exist_ok=True)
    zip_path = DIST / "open-provenance-knowledge-0.1.0.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in FILES:
            info = zipfile.ZipInfo(relative, date_time=(2026, 7, 28, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (ROOT / relative).read_bytes(), compresslevel=9)
    tar_path = DIST / "open-provenance-knowledge-0.1.0.tar.gz"
    with tar_path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=EPOCH, compresslevel=9) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for relative in FILES:
                    info = archive.gettarinfo(ROOT / relative, arcname=relative)
                    info.mtime = EPOCH
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    with (ROOT / relative).open("rb") as handle:
                        archive.addfile(info, handle)
    for relative in FILES[:4]:
        target = DIST / Path(relative).name
        target.write_bytes((ROOT / relative).read_bytes())


if __name__ == "__main__":
    main()
