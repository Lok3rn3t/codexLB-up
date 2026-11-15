# Fork release

The user requested a GitHub prerelease and a separately named PyPI package for
Lok3rn3t/codexLB-up. The upstream `codex-lb` namespace must remain independent.
The first fork candidate is `v1.25.0-beta.10` (`1.25.0b10` on PyPI).

The Trusted Publisher configuration is GitHub owner `Lok3rn3t`, repository
`codexLB-up`, workflow `release.yml`, environment `pypi`. Package-name
normalization follows Python packaging rules; import packages and console
commands retain their established names. Installing both distributions into
one Python environment would overlap their `app` module and commands, so use
an isolated environment or `uvx --from codexLB-up==1.25.0b10 codex-lb`.

The two frontend failures found during release validation are unchanged
upstream assertions with US-formatted numeric literals. Expected strings must
use the same locale-sensitive formatting contract as the existing UI.

The fork's default branch is `codexLB-up`. This initial fork release uses an
explicit version tag and OIDC publishing, without the upstream
`RELEASE_PLEASE_TOKEN` setup. Inherited release-please automation and container
publishing jobs are restricted to the upstream repository. The CI push trigger
tracks the fork branch, while the inherited `main` branch remains available.
The fork-specific distribution guide is the package's PyPI long description.

Validation uses local release-tooling regressions, the installed wheel and its
packaged migrations/static assets, frontend build/lint, and workflow lint.
Provider traffic and Nix builds are outside this release verification.

Observed verification: 68 release-tooling tests passed; 26 telemetry tests
passed; both locale-sensitive UI suites passed (12 tests); frontend build and
lint passed. Fork wheel/sdist passed Twine, included 84 JS and one CSS asset,
and the installed-wheel smoke passed migrations, CLI, health, and static routes.
Actionlint passed for all changed workflows. The complete frontend suite is
also rerun after the assertion fixes, with its result recorded in release notes.
