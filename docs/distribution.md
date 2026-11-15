# codexLB-up

codexLB-up is a maintained fork of [Soju06/codex-lb](https://github.com/Soju06/codex-lb),
a load balancer and OpenAI-compatible proxy for ChatGPT accounts with a usage
dashboard. This distribution includes audited security and compatibility fixes.
It is published independently by [Lok3rn3t](https://github.com/Lok3rn3t/codexLB-up).

## Install and run

Requires Python 3.13 or newer. Run the beta in an isolated environment with uv:

```sh
uvx --from "codexLB-up==1.25.0b10" codex-lb
```

Or install it inside a dedicated Python virtual environment:

```sh
python -m pip install "codexLB-up==1.25.0b10"
codex-lb --help
codex-lb
```

The distribution name is `codexLB-up`; its commands remain `codex-lb` and
`codex-lb-db`. Use a separate environment from the upstream `codex-lb` package,
because both distributions provide the same Python modules and commands.
The wheel and source distribution include the compiled dashboard.

## Releases and source

See [GitHub Releases](https://github.com/Lok3rn3t/codexLB-up/releases) for the
fix list, verification results, and downloadable packages. Beta versions are
prereleases. The first fork release publishes Python packages and a GitHub
prerelease; Docker images and Helm charts are not part of this publication.

The original project and its contributors retain their attribution and MIT
license. General configuration documentation is inherited from upstream; use
the fork's installation command above to install this distribution.

Release contract: [OpenSpec release-management specification](https://github.com/Lok3rn3t/codexLB-up/blob/codexLB-up/openspec/specs/release-management/spec.md).
