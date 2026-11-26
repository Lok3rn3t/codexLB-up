# Allow an explicit prerelease rebuild without PyPI

## Why

The owner requested replacement of the withdrawn 1.26.0-beta.1 prerelease.
Its original publication run uploaded Python distributions successfully; PyPI
version filenames cannot safely be reused for changed code. Docker, Helm and
GitHub assets still need their normal build and runtime gates.

## What Changes

- Add an explicit manual-dispatch option to omit PyPI for prereleases only.
- Retain build, architecture smoke, upgrade and vulnerability gates.
- Omit PyPI install commands when PyPI publication was intentionally skipped.
- Keep normal tag publication and all stable publication behavior unchanged.

## Impact

- Affected spec: release-management.
- Affected code: release metadata CLI and Release workflow.
- Replacing an existing tag or container tag is a separate owner-authorized operation.
