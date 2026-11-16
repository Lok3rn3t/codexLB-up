# Native platform checks verified

Local manifest-selection and smoke-script regressions: 27 passed. The combined
release-version, platform-selection, and smoke regression run passed 64 cases.
Ruff, formatting, Ty, Bash syntax, actionlint, and strict OpenSpec validation
passed.

Release run `43854085727` passed on the final source
`5007c731738140aaabc0f6e4b53b5da0673cccb2`:

- Native amd64 smoke job `133254770325`: startup, version, native IPC, health, and 15 assets passed.
- Native ARM64 smoke job `133254770353`: the same assertions passed without QEMU.
- Upgrade/security/promotion job `133255091726`: original beta.9 upgrade and restart, Trivy severity gates, and complete-index alias promotion passed.
- PyPI and stable GitHub publication followed these gates successfully.

The earlier parent-index collision was resolved by child-manifest selection.
The subsequent QEMU readiness failure did not reproduce on native ARM64. The
readiness deadline and application assertions were not weakened. Public OCI
configs for both children match the final release revision and architecture;
all promoted aliases retain the same multiarchitecture parent index.
