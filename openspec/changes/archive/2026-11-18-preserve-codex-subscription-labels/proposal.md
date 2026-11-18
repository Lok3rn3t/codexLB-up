## Why

The account dashboard renders `Prolite` for Business Premium because account
metadata collapses `self_serve_business_prolite` into `prolite`. Official Codex
keeps these identifiers separate and displays Business Premium and Pro 100.

## What Changes

- Preserve upstream Business Premium identity in stored account metadata and
  dashboard responses while retaining existing policy normalization.
- Use the status and analytics subscription labels from OpenAI Codex commit
  `ca21fe65d18a9b6326759fb4263c65dfbb645aa5` in a shared UI formatter.
- Apply status labels consistently across account surfaces and request logs,
  including displayed-label search and sorting.
- Recover previously collapsed account metadata only through a fresh accepted
  upstream observation; never infer Business Premium from `prolite` alone.

## Impact

Account metadata normalization, usage identity comparisons, frontend plan labels,
and regression coverage. No schema migration, capacity estimate changes, new
entitlements, production changes, or release replacement are required.
