# codexLB-up

codexLB-up is a maintained fork of [Soju06/codex-lb](https://github.com/Soju06/codex-lb),
a load balancer and OpenAI-compatible proxy for ChatGPT accounts with a usage
dashboard. This distribution includes audited security and compatibility fixes.
It is published independently by [Lok3rn3t](https://github.com/Lok3rn3t/codexLB-up).

## Install and run

Requires Python 3.13 or newer. Run the release in an isolated environment with uv:

```sh
uvx --from "codexLB-up==1.25.0" codex-lb
```

Or install it inside a dedicated Python virtual environment:

```sh
python -m pip install "codexLB-up==1.25.0"
codex-lb --help
codex-lb
```

The distribution name is `codexLB-up`; its commands remain `codex-lb` and
`codex-lb-db`. Use a separate environment from the upstream `codex-lb` package,
because both distributions provide the same Python modules and commands.
The wheel and source distribution include the compiled dashboard.

## Docker

Published images support Linux `amd64` and `arm64` and include the native egress
worker. Stable releases publish exact version, major/minor, and `latest` tags.

```sh
docker volume create codex-lb-data
docker network inspect codex-lb-net >/dev/null 2>&1 || docker network create codex-lb-net
docker run -d --name codex-lb --restart unless-stopped \
  --network codex-lb-net \
  -p 2455:2455 -p 1455:1455 \
  -v codex-lb-data:/var/lib/codex-lb \
  ghcr.io/lok3rn3t/codexlb-up:1.25.0
```

Open the dashboard at `http://localhost:2455`. The volume stores the database,
encryption key, and account data. Docker Compose examples are available in the
[repository](https://github.com/Lok3rn3t/codexLB-up/blob/codexLB-up/docker-compose.prod.yml).

## Helm

The chart uses the fork image by default and is published to GHCR:

```sh
helm pull oci://ghcr.io/lok3rn3t/charts/codex-lb --version 1.25.0
```

Follow the [chart installation guide](https://github.com/Lok3rn3t/codexLB-up/blob/codexLB-up/deploy/helm/codex-lb/README.md)
for bundled or external PostgreSQL and cluster configuration.

## Releases and source

See [GitHub Releases](https://github.com/Lok3rn3t/codexLB-up/releases) for the
fix list, verification results, and downloadable packages. Stable releases
publish PyPI packages, Docker images, a Helm chart, and a GitHub Release.

The original project and its contributors retain their attribution and MIT
license. General configuration documentation is inherited from upstream; use
the fork's installation command above to install this distribution.

Release contract: [OpenSpec release-management specification](https://github.com/Lok3rn3t/codexLB-up/blob/codexLB-up/openspec/specs/release-management/spec.md).
