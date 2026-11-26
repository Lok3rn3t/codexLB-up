## Implementation and verification

- [x] Dispatch the artifact workflow for the validated tag with the repository token.
- [x] Check tag reuse, conflicting tags, and dispatch inputs. An isolated Git remote and a mock GitHub CLI covered first publication, retry after dispatch failure, tag reuse, tag conflicts and the upstream PyPI path.
- [x] Validate the release specifications and workflows. Actionlint, strict OpenSpec validation and the release guard and workflow regression tests passed.
