# codexLB-up

codexLB-up is a maintained fork of [Soju06/codex-lb](https://github.com/Soju06/codex-lb),
a load balancer and OpenAI-compatible proxy for ChatGPT accounts with a usage
dashboard. This distribution includes audited security and compatibility fixes.
It is published independently by [Lok3rn3t](https://github.com/Lok3rn3t/codexLB-up).

## Install and run

Requires Python 3.13 or newer. Run the release in an isolated environment with uv:

```sh
uvx --from "codexLB-up==1.27.0" codex-lb
```

Or install it inside a dedicated Python virtual environment:

```sh
python -m pip install "codexLB-up==1.27.0"
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
  ghcr.io/lok3rn3t/codexlb-up:1.27.0
```

Open the dashboard at `http://localhost:2455`. The volume stores the database,
encryption key, and account data. Docker Compose examples are available in the
[repository](https://github.com/Lok3rn3t/codexLB-up/blob/codexLB-up/docker-compose.prod.yml).

## Helm

The chart uses the fork image by default and is published to GHCR:

```sh
helm pull oci://ghcr.io/lok3rn3t/charts/codex-lb --version 1.27.0
```

Follow the [chart installation guide](https://github.com/Lok3rn3t/codexLB-up/blob/codexLB-up/deploy/helm/codex-lb/README.md)
for bundled or external PostgreSQL and cluster configuration.

## Upgrading from the original beta.9

The supported source is upstream `codex-lb==1.25.0b9`, whose Docker tag is
`ghcr.io/soju06/codex-lb:1.25.0-beta.9`. The target is
`ghcr.io/lok3rn3t/codexlb-up:1.27.0`. Keep the existing database engine,
data mounts, encryption key, environment, published ports, and Docker networks.
There is no need to export and re-import accounts or create another database.

This is an application upgrade with existing schema updates, not a PostgreSQL
major-version upgrade or a SQLite-to-PostgreSQL conversion. All 261 beta.9
migration files are retained unchanged. Three inherited revisions add SCIM
storage, remove the retired subscription-overflow storage, and merge their
revision heads. The old application must stop before those updates run; it
cannot safely use the upgraded schema. Retired overflow fields are not retained
in the live schema, so keep the backup if you used that withdrawn feature.

### Single container with SQLite

These Bash commands cover the original upstream Docker quick start: a container
named `codex-lb`, data at `/var/lib/codex-lb`, ports 2455/1455, and network
`codex-lb-net`. If you customized the launch, use your existing ports and networks
and include the same `-e`, `--env-file`, additional mounts, and other runtime
options in both the upgrade and rollback commands. If your data directory or
key lives elsewhere, back up those paths too. Do not replace custom settings
with the examples.

Download the release before stopping the application. Inspect its mounts and
save the container configuration locally; the saved configuration can contain
secrets and must not be shared publicly.

```bash
set -e
docker pull ghcr.io/lok3rn3t/codexlb-up:1.27.0
docker inspect codex-lb --format '{{.Config.Image}}'
docker inspect codex-lb --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}'

umask 077
backup_dir="$(mktemp -d "$PWD/codex-lb-backup.XXXXXX")"
mkdir "$backup_dir/data"
docker inspect codex-lb > "$backup_dir/container.json"
docker inspect codex-lb --format '{{.Image}}' > "$backup_dir/image-id"
docker stop --time 60 codex-lb
docker cp -a codex-lb:/var/lib/codex-lb/. "$backup_dir/data/"
test -s "$backup_dir/data/store.db"
test -s "$backup_dir/data/encryption.key"
printf 'Backup saved to %s\n' "$backup_dir"
```

Keep the stopped original container as a reference. Reuse its volumes with
`--volumes-from`, so the new application receives the actual existing data even
if the volume has a different name. Add your original environment and other
custom options here if applicable.

```bash
docker rename codex-lb codex-lb-upstream-backup
docker run -d --name codex-lb --restart unless-stopped \
  --network codex-lb-net \
  -p 2455:2455 -p 1455:1455 \
  --volumes-from codex-lb-upstream-backup \
  ghcr.io/lok3rn3t/codexlb-up:1.27.0

docker logs --tail 100 codex-lb
curl --fail --retry 30 --retry-delay 2 --retry-all-errors \
  --retry-max-time 120 --max-time 5 http://127.0.0.1:2455/health/ready
docker exec codex-lb python -c 'import app; print(app.__version__)'
```

Then sign in with the existing dashboard credentials and verify your accounts,
API keys, settings, and history. Make a normal client request. Keep the backup
until that verification is complete. Existing client URLs remain the same.
Active streams disconnect during the restart and may need a client retry.

The default entrypoint applies the inherited schema updates before serving.
`CODEX_LB_DATABASE_MIGRATE_ON_STARTUP=false` deliberately prevents that step;
beta.9's older schema then fails startup. If schema changes are prohibited,
keep that setting and the old image until a separate upgrade is approved. Do
not bypass the mismatch with `stamp`, deletion of `store.db`, or a new empty
volume. The documented transition does not require a PostgreSQL upgrade.

### Rollback

After the new image has upgraded the schema, do not simply restart the original
container against that volume. Restore the backup into a **new** volume and
launch the exact original image recorded above. This retains the failed
container and upgraded data for inspection. The example uses the same shell's
`backup_dir`; set it to the printed backup path if you opened a new shell.
Changes made after the backup will not be present in the restored instance.

```bash
docker stop --time 60 codex-lb
docker rename codex-lb codex-lb-upgrade-failed
rollback_volume="codex-lb-rollback-$(date +%Y%m%d%H%M%S)"
docker volume create "$rollback_volume"
docker create --name codex-lb --restart unless-stopped \
  --network codex-lb-net \
  -p 2455:2455 -p 1455:1455 \
  -v "$rollback_volume:/var/lib/codex-lb" \
  "$(cat "$backup_dir/image-id")"
docker cp -a "$backup_dir/data/." codex-lb:/var/lib/codex-lb/
docker start codex-lb
```

For external PostgreSQL, keep the existing `CODEX_LB_DATABASE_URL`, PostgreSQL
server/version, and encryption key. The filesystem backup above does not back
up PostgreSQL: make a consistent database backup before upgrading and restore
that backup for rollback. Do not run the repository's `postgres-upgrade`
profile as part of this image change. The dedicated beta.9 container check uses
SQLite; external database deployments require their own backup and rehearsal.

## Releases and source

See [GitHub Releases](https://github.com/Lok3rn3t/codexLB-up/releases) for the
fix list, verification results, and downloadable packages. Validated releases
publish PyPI packages, Docker images, a Helm chart, and a GitHub Release.

The original project and its contributors retain their attribution and MIT
license. General configuration documentation is inherited from upstream; use
the fork's installation command above to install this distribution.

Release contract: [OpenSpec release-management specification](https://github.com/Lok3rn3t/codexLB-up/blob/codexLB-up/openspec/specs/release-management/spec.md).
