# Stable publication verified

Published on 2026-11-16 from `5007c731738140aaabc0f6e4b53b5da0673cccb2`.
The stable tag is immutable after Python publication.

The [full CI run](https://github.com/Lok3rn3t/codexLB-up/actions/runs/43854074995)
on that exact source passed all 27 jobs, including the required aggregate,
backend/frontend tests, Docker, Helm, Rust, Nix, and migration checks. Release
guards and simplicity budgets also passed.

- [Release workflow](https://github.com/Lok3rn3t/codexLB-up/actions/runs/43854085727): successful, including native amd64 and ARM64 startup, native-worker IPC, health, migrations, and 15 dashboard assets on each platform.
- Original upstream beta.9 image upgrade and restart passed in job `133255091726`, preserving the synthetic volume, credentials, settings, and history. Trivy gates and image promotion also passed.
- [GitHub Release](https://github.com/Lok3rn3t/codexLB-up/releases/tag/v1.25.0): public, stable, latest, English notes, wheel, sdist, Helm archive, and `SHA256SUMS.txt`.
- [PyPI](https://pypi.org/project/codexLB-up/1.25.0/): Trusted Publishing succeeded; both file hashes match the downloaded build and GitHub assets.
- Public GHCR image tags `1.25.0`, `latest`, `1.25`, and `1` all resolve to `sha256:0a0fbe93ce48c93aec673f955748a9c34c8f0674189656470a74978e4b9d508c`. Both executable configs contain the exact release revision and correct architecture/version.
- Public Helm chart `1.25.0` has matching chart/app versions and the fork image defaults. Its OCI package is byte-identical to the release asset.

## Artifact SHA-256 checksums

| File | SHA-256 |
| --- | --- |
| `codexlb_up-1.25.0-py3-none-any.whl` | `96371d1d91d997a7c17d353093615980a6c0da1b9650ad8f5556045a4cf4be4a` |
| `codexlb_up-1.25.0.tar.gz` | `43989c8467f30a76c08d09174b16fa63841be6ee4c31d331a86a0e5dca00d213` |
| `codex-lb-1.25.0.tgz` | `bf97c66da8668e20296dd2392e118e9730f586679a0d71b676647cddf3d7317c` |

The maintainer requested clearing previous releases, tags, and Actions history.
Old metadata and failure logs were preserved locally before cleanup. Only the
new stable release/tag is retained; the changelog uses a commit base so removing
the beta tag does not break the comparison. New successful verification runs
remain as evidence. Source commit history was not rewritten.

These checks use isolated disposable data. No production container or database
was changed, and no live provider-inference or production-load claim is made.
