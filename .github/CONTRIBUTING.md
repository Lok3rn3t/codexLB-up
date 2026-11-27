# Contributing to codexLB-up

Contributions to `Lok3rn3t/codexLB-up` are welcome. You can propose bug fixes,
features, tests, documentation, dependency updates, and reviewed upstream fixes.
This guide covers creating a branch, committing changes, and submitting a pull
request to the `codexLB-up` base branch.

Anyone can commit to their own fork and submit a PR here. Contributors with
write access can push a topic branch directly to this repository. Maintainers
review and merge contributions using the gates below.

Write commit messages, PR titles and descriptions, and documentation in English.

If anything below is unclear or out of date, please open a small `docs:` PR —
that's the easiest first contribution.

---

## Table of contents

1. [Code of conduct](#code-of-conduct)
2. [Ways to contribute](#ways-to-contribute)
3. [Development setup](#development-setup)
4. [Project layout](#project-layout)
5. [Workflow: OpenSpec-first](#workflow-openspec-first)
6. [Coding conventions](#coding-conventions)
7. [Commit & PR conventions](#commit--pr-conventions)
8. [Merge gates and collaborator rules](#merge-gates-and-collaborator-rules)
9. [Tests](#tests)
10. [Release process](#release-process)
11. [Security issues](#security-issues)

---

## Code of conduct

This project does not ship a formal code of conduct document. Be respectful
and constructive in issues, discussions, and reviews; maintainers may moderate
or remove content that is not.

## Ways to contribute

You don't need to write code to help:

- **Triage**: reproduce open issues, ask for missing details, add labels.
- **Docs**: improve the README, fix typos, document a deployment recipe.
- **Discussions**: answer "how do I…?" questions in the upstream project's
  [GitHub Discussions](https://github.com/Soju06/codex-lb/discussions).
- **Bug reports**: include reproduction steps, the affected version, and
  sanitized logs in your fix PR. Link an upstream issue when one exists.
- **Feature ideas**: use a draft PR to explain the proposed behavior and share
  an initial implementation for feedback.
- **Code**: fix a bug, implement a feature, refactor a hot spot.
- **Upstream fixes**: link the original PR or commit, preserve attribution, and
  explain how you verified the change against this fork.

For problems shared with upstream, look for issues labelled
[`good first issue`](https://github.com/Soju06/codex-lb/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22) or
[`help wanted`](https://github.com/Soju06/codex-lb/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22)
if you're looking for a starter task.

## Development setup

codex-lb is a Python project managed with [`uv`](https://docs.astral.sh/uv/).
The commands below use Git and Python 3.13 or newer. Frontend work also uses Bun.
The `make` targets use a Bash-compatible environment, such as Linux, macOS,
or WSL on Windows.

### Clone and create a branch

Fork `Lok3rn3t/codexLB-up` on GitHub, then clone your fork. Replace
`YOUR-USERNAME` with your GitHub username and use your fork's repository name
if you chose a different one. In these commands, `origin` is your fork and
`upstream` is `Lok3rn3t/codexLB-up`.

```bash
git clone https://github.com/YOUR-USERNAME/codexLB-up.git
cd codexLB-up
git remote add upstream https://github.com/Lok3rn3t/codexLB-up.git
git fetch upstream
git switch --no-track -c docs/update-guide upstream/codexLB-up
```

If you have write access, you can clone this repository and create a topic
branch from `origin/codexLB-up` instead.

```bash
git clone https://github.com/Lok3rn3t/codexLB-up.git
cd codexLB-up
git fetch origin
git switch --no-track -c docs/update-guide origin/codexLB-up
```

`docs/update-guide` is an example branch name. Choose a name that describes
your change, such as `fix/stream-timeout` or `feat/account-filter`.

### Install dependencies

```bash
uv sync --frozen --dev
uv run pre-commit install

# Inspect the backend command
uv run codex-lb --help
```

For frontend changes, install the locked dependencies with Bun.

```bash
cd frontend
bun install --frozen-lockfile
cd ..
```

The README's [Development section](../README.md#development) shows how to
start the backend and dashboard locally.

## Project layout

```
.
├── app/                  # Python application (proxy, accounts, dashboard backend)
├── frontend/             # Dashboard SPA
├── deploy/helm/codex-lb/ # Helm chart
├── tests/
│   ├── unit/             # Fast, isolated tests
│   └── integration/      # End-to-end / network-touching tests
├── openspec/             # SSOT — specs, change proposals, archived changes
│   ├── specs/<capability>/
│   └── changes/<change>/
└── .github/              # Issue forms, PR template, workflows
```

## Workflow: OpenSpec-first

codex-lb uses **OpenSpec as the source of truth** for change-driven development.
You don't have to author OpenSpec entries for trivial fixes, but for anything
that changes observable behavior, requirements, contracts, or schema, an
OpenSpec change is expected.

The typical flow:

1. Find the relevant spec in `openspec/specs/<capability>/spec.md`.
2. If your change alters behavior: create
   `openspec/changes/<kebab-case-change>/` with a proposal + tasks.
3. Implement the tasks; keep `spec.md` in sync.
4. Validate: `openspec validate --specs`.
5. Verify and archive when done.

If you're unsure whether your PR needs an OpenSpec change, open it as draft
and ask — a maintainer will tell you.

Maintainers handle `CHANGELOG.md` and release notes during release preparation.

## Coding conventions

- **Python**: 3.13+. Code is formatted with `ruff format`, linted with
  `ruff check`, and type-checked with `ty` (Astral's type checker).
- **Imports / style**: follow what you see in nearby files; the linter is
  authoritative — if `ruff` and your style guide disagree, ruff wins.
- **Type hints**: required on new public functions and new modules. Existing
  code is being typed incrementally.
- **Logging**: prefer the project's structured logger over `print`.
- **Secrets**: never commit API keys, tokens, account credentials, or `.env`
  files. The CI redaction is best-effort, not a safety net.

Run the full lint/test gate locally before pushing:

```bash
uv run pre-commit run local-ci --hook-stage manual --all-files
```

The `local-ci` hook runs `make ci`, which is the local
version of the GitHub Actions CI gate. You can also run a single CI job while
iterating, for example:

```bash
make lint
make test-unit
make package
```

## Commit & PR conventions

codexLB-up uses **[Conventional Commits](https://www.conventionalcommits.org/)**
to make the purpose of each change clear and support release tooling.

Format:

```
<type>(<scope>)?: <subject>

[optional body]

[optional footer(s)]
```

Common `type`s:

| Type        | When to use it                                            |
|-------------|-----------------------------------------------------------|
| `fix`       | Bug fix → patch version bump                              |
| `feat`      | New user-facing feature → minor version bump              |
| `refactor`  | Internal change, no behavior change                       |
| `perf`      | Performance improvement                                   |
| `docs`      | Documentation only                                        |
| `test`      | Test-only change                                          |
| `build`     | Build system / packaging                                  |
| `ci`        | CI configuration                                          |
| `chore`     | Tooling / maintenance with no user-visible effect         |

Common `scope`s used in this repo: `proxy`, `accounts`, `auth`, `oauth`,
`quota`, `chat`, `proxy-responses`, `dashboard-auth`, `ui`, `db`, `types`,
`openspec`, `main` (release).

**Breaking changes**: append `!` after the type/scope and/or add a
`BREAKING CHANGE:` footer.

Examples (from the actual repo history):

```
fix(proxy): handle model fetch timeouts
fix(accounts): recover quota status from usage refresh
feat(proxy): add OpenAI-compatible /v1/images API (gpt-image-2 via image_generation tool)
fix(dashboard-auth): reject passwords longer than bcrypt's 72-byte limit
```

PR titles follow the same format and become the squash-merge commit title.

### Pull request flow

1. Create a topic branch from the latest `codexLB-up` branch using the
   [setup instructions](#clone-and-create-a-branch).
2. Make atomic commits with Conventional Commit titles.
3. Run the lint/test gate locally (see above).
4. Open a PR against `Lok3rn3t/codexLB-up`, base branch `codexLB-up`, using
   the template. Explain the problem, the change, and your validation. Link
   the relevant issue when one exists, using `Soju06/codex-lb#N` for an
   upstream issue.
5. CodeRabbit (and a human maintainer) will review. Address feedback by
   pushing follow-up commits — no force-pushing during active review.
6. Once approved and CI is green, a maintainer squash-merges with a clean
   Conventional Commits title.

For example, after editing `README.md`, inspect and commit that file, then
push your topic branch.

```bash
git status --short
git diff -- README.md
git add README.md
git diff --cached
git commit -m "docs(readme): clarify local development"
git push -u origin docs/update-guide
```

Use **Compare & pull request** on GitHub. Select `Lok3rn3t/codexLB-up` as
the base repository and `codexLB-up` as the base branch. Select your fork
or this repository as the head repository, and your topic branch as the
compare branch.

With GitHub CLI, a contributor using a personal fork can open the same PR
with the following command. The interactive prompts accept the title and
description.

```bash
gh pr create --repo Lok3rn3t/codexLB-up --base codexLB-up --head YOUR-USERNAME:docs/update-guide
```

For a branch pushed directly to this repository, use `--head docs/update-guide`.
Add `--draft` if you want feedback while the work is in progress. Use the
[PR template](pull_request_template.md) to describe the change and checks.

To address review feedback, create another commit on the same topic branch
and run `git push`. GitHub adds the commit to the existing PR and reruns the
applicable checks. GitHub's guide explains the fork and base branch controls
in more detail. [Creating a PR from a fork](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request-from-a-fork)

## Merge gates and collaborator rules

These rules apply to **every PR**, regardless of author (external
contributor, project owner, or collaborator). They formalize the review
bar that has produced the current proxy / continuity-recovery / OpenSpec
quality so far.

### Merge gates

Before a PR is squash-merged into `codexLB-up`:

1. **CI must be all-green** on the merge-target head. "UNSTABLE, looks
   fine" is not a green CI; rerun, fix, or wait. The Helm / migration /
   PostgreSQL test jobs are part of the gate, not optional. The
   `CI Required` check is the branch-protection check to require: it
   depends on every `ci.yml` job and also runs for merge queue synthetic merge
   groups, so a stale PR head cannot bypass a broken merge result. The release
   guards (`Beta release guard`, `Stable release guard`) run from
   `release-guards.yml` so an edited release PR body re-checks them without
   restarting the matrix; they are separate contexts, not part of `CI Required`.
2. **Actionable CodeRabbit findings must be fixed or explicitly addressed
   or dismissed in-thread on the merge-target head.** Review the current-head
   CodeRabbit findings before merging; no finding may be silently skipped.
   A local Codex review against the latest `codexLB-up` branch provides
   additional feedback alongside the required review.
   - **P1 findings**: fix in the PR, or justify in-thread with a short
     write-up of why the finding doesn't apply. No silent skipping.
   - **P2 findings**: fix in the PR, or open a follow-up issue and link
     it in the PR thread before merging.
3. **`mergeable` must be `CLEAN`** in the GitHub API — no merge
   conflicts, no requested-changes review still outstanding, no missing
   required status check.
4. **OpenSpec change folder for behavior changes** (see
   [Workflow: OpenSpec-first](#workflow-openspec-first)). Pure
   refactors, docs-only edits, dev-tool changes, and test stabilization
   PRs are exempt; everything else needs an `openspec/changes/<slug>/`
   entry.
5. **`Fixes #N` / `Closes #N` in the PR body** for anything that
   resolves an issue, so the issue close stays automatic and the merge
   stays traceable. Use `Refs #N` / `Related to #N` for partial cover.
6. **Simplicity gates must pass** (see
   [Simplicity gates](#simplicity-gates)): the six simplicity rules
   (PRINCIPLES.md P1-P6). Budget exceptions need the
   maintainer-applied `simplicity-budget-approved` label.

### Simplicity gates

These implement [PRINCIPLES.md](../PRINCIPLES.md); the normative spec is
`openspec/specs/contribution-simplicity/spec.md`. Reviewers apply them to
every PR (budget checks are enforced by CI via
`.github/workflows/simplicity-budgets.yml`):

1. **New features default to off or zero-config.** No new required
   setup step (env var, migration action, external account, manual
   file edit) on the base install path without maintainer approval via
   the `simplicity-budget-approved` label.
2. **Every new `CODEX_LB_*` setting justifies not being a default.**
   The PR body answers "why can't this be a hardcoded default?" for
   each new setting; internals-only knobs stay out of `.env.example`.
3. **README, `.env.example`, and dashboard nav are budgeted.** The
   caps live in `.github/simplicity-budgets.toml`. Exceeding a cap
   requires the maintainer-applied `simplicity-budget-approved` label
   before merge.
4. **Feature docs go to `docs/` + OpenSpec, never new README
   sections.** Each spec-governed docs page links back to its
   `openspec/specs/<capability>/` entry.
5. **Dashboard-visible PRs include before/after screenshots** (or a
   short recording) in the PR body.
6. **The dashboard is the primary configuration surface** (PRINCIPLES.md
   P6). Every new setting names its tier (T0 bootstrap / T1 instance
   topology / T2 secret / T3 behaviour tunable / T4 incident debug) in the
   PR body; a T3 setting has a `dashboard_settings` column, not an
   env-only home; precedence stays code default < env < dashboard with no
   env-wins paths. Machine-checked by `scripts/check_settings_tiers.py`
   under `make lint`; the normative spec is linked from
   [PRINCIPLES.md P6](../PRINCIPLES.md#p6--the-dashboard-is-the-primary-configuration-surface).

### Collaborator rules

Collaborators (write-access contributors) follow two additional rules on
top of the merge gates above:

1. **No self-merge by default.** A collaborator's own PR is merged by
   another maintainer (or, until the project has more collaborators,
   by the project owner). Review independence matters more than
   turnaround.
2. **Large PRs get split.** Roughly:
   - If a PR is a stack tip pulling in unrelated commits from sibling
     branches, split it so each merged PR is a single scoped change.
   - If a single PR is over **~800 net lines** and spans multiple
     concerns, split it into reviewable pieces. A single 1500-line
     change scoped to one capability is fine; a 400-line change that
     touches the proxy hot path *and* the dashboard *and* the OAuth
     flow is not.

### Bus factor escape hatch

To keep the project unblocked if the owner is unavailable, the following
self-merge escape hatch applies:

- If a collaborator's PR has been waiting on a maintainer merge for
  **more than 14 days** with **all merge gates met** (CI green,
  CodeRabbit findings addressed, `mergeable=CLEAN`, no
  outstanding requested-changes review, no objection from any other
  active collaborator in the thread), the PR author may self-merge.
- Self-merge under this clause **must** include a comment on the PR
  explicitly invoking the clause and linking to the date the merge
  gates first went green. Audit trail must stay clean.
- The clause is a safety valve, not a default path. If you're tempted to
  invoke it on a PR you opened less than two weeks ago, the merge gates
  probably aren't actually all green yet.

### What this is not

These rules are intentionally lightweight. They don't require:

- A second human reviewer in addition to CodeRabbit for every PR.
  CodeRabbit review + the PR author + a maintainer merge is the baseline.
- Squash-merge commit message rewriting beyond the Conventional Commits
  title. The PR description ends up in the body; that's enough.
- A formal escalation process for disagreements. If a P1 finding is
  disputed, work it out in-thread; if it can't be resolved, leave the
  PR open and ping the owner.

## Tests

- **Unit tests** live under `tests/unit/` and should be fast and hermetic.
- **Integration tests** live under `tests/integration/` and may spin up the
  app, hit local sockets, or use fixtures that mimic upstream.
- New behavior needs at least one unit test. New endpoints need an
  integration test.
- Run a focused subset with:

```bash
uv run pytest tests/unit/test_proxy_api_responses_contract.py -q
```

## Release process

Maintainers coordinate releases after changes reach `codexLB-up`. They
prepare the release-managed versions and tag, then use the
[release workflow](workflows/release.yml) to build and publish artifacts.
The distribution and channel requirements are documented in
[release management](../openspec/specs/release-management/spec.md).

Ordinary contribution PRs focus on their change. Maintainers handle version
bumps, tags, changelog generation, and publication as part of a release.

### Release channels: beta first

Stable releases are promoted from the beta channel, not cut directly:

1. A `vX.Y.Z-beta.N` release ships first (the beta release PR).
2. The beta soaks on at least one production-scale deployment for **at least
   48 hours** with no new regressions attributable to the release.
3. Only then is the stable `vX.Y.Z` release PR merged.

Rationale: migrations and proxy-path changes routinely behave differently at
production data volumes than in CI. The beta soak is where migration duration,
memory pressure, and upstream-protocol regressions surface without burning a
stable version number.

Exceptions — a maintainer may promote directly to stable, noting the reason in
the release PR, when the **entire** unsoaked delta consists of (any
combination of):

- documentation, CI, or release-tooling changes, or
- a security or outage hotfix where waiting out the soak is the greater risk.

A train that also carries unrelated unsoaked changes must either soak as a
beta or ship the hotfix separately.

Before merging a release PR whose train includes migrations, inspect the
Alembic revisions directly (`git diff vPREV..HEAD -- app/db/alembic/versions`)
for data backfills and estimate their duration against a production-sized
dataset — they run at startup and block serving until they finish. Changelog
titles do not reveal backfills.

The normative requirements live in
[`openspec/specs/release-management/`](../openspec/specs/release-management/).

## Security issues

Please do **not** open public issues for security vulnerabilities. Report them
privately via
[GitHub Security Advisories](https://github.com/Soju06/codex-lb/security/advisories/new).
See [SECURITY.md](./SECURITY.md) for full details.

---

Happy hacking. If you get stuck, open a draft PR or start a Discussion —
maintainers would rather see a half-finished idea than no idea at all.
