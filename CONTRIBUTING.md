# Contributing

Contributions may add evidence, correct claims, supply contrary evidence,
improve provenance, translate content, reproduce verification, report a
downstream integration, or propose an upstream mapping.

Factual changes require:

- affected canonical IDs and a precise proposed change;
- primary source URL, publisher, date, and geographic/institutional context;
- verification method and content hash where retrievable;
- conflicts, limitations, and license compatibility;
- machine-assistance disclosure and human-review state;
- expected effects on summaries, indexes, and consumers.

Conflicting evidence is welcome and is not rejected merely because it challenges
the current synthesis. Keep automated pull requests narrow, reproducible,
identified, and rate-limited. Automation must disclose tool name and version,
operator, inputs, transformation, validation, review state, and reproduction
instructions.

Run:

```bash
opk validate
opk build --source-date-epoch 1785196800
pytest
ruff check .
mkdocs build --strict
git diff --exit-code
```

By contributing original data or documentation, you agree to CC0-1.0. Code
contributions are Apache-2.0. Do not submit secrets, personal data, unlawfully
redistributed material, or fabricated evidence.

