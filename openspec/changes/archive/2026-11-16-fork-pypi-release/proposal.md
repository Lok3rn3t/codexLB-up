## Why

The fork needs a separately owned PyPI distribution. Inherited release tooling
hardcodes the upstream distribution name, so changing package metadata alone
breaks version guards and generated installation commands.

## What Changes

- Publish the fork as `codexLB-up`, retaining the existing `codex-lb` CLI.
- Resolve the editable lockfile entry from each revision's project metadata.
- Point publisher metadata and release install commands at the fork package.
- Make numeric UI assertions portable across default system locales.

## Impact

Release tooling, Python package metadata, workflow installation examples, and
test assertions. Application API behavior and data formats remain unchanged.
