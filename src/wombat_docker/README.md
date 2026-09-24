# wombat_docker

Containerized manatee validator application.

## Prerequisites

- Linux host for image build workflow
- Docker
- Access to /var/wombat mount paths on host
- PostgreSQL reachable from container

## Build

Preferred helper script:

```bash
./docker_build.sh
```

Manual build:

```bash
docker build \
  --build-arg WOMBAT_UID=$(id -u wombat) \
  --build-arg WOMBAT_GID=$(id -g wombat) \
  -t manatee:latest \
  src/wombat_docker
```

## Run

Default mode (validator):

```bash
docker run -v /var/wombat:/mnt/wombat --name manatee manatee:latest
```

Explicit validator mode:

```bash
docker run -e stuntbox=validator -v /var/wombat:/mnt/wombat --name manatee manatee:latest
```

## Environment Variables

Set via Dockerfile defaults unless overridden:

- FAILURE_DIR=/mnt/wombat/failure
- FRESH_DIR=/mnt/wombat/fresh/manatee
- SUCCESS_DIR=/mnt/wombat/manatee/success
- DB_CONN=postgresql+psycopg2://manatee_client:batabat@172.17.0.1:5432/manatee
- PG_CONNECT_TIMEOUT=5
- PG_STATEMENT_TIMEOUT_MS=5000

## Test

Run all tests from this directory:

```bash
./venv/bin/python -m pytest -q
```

Or run validator-focused script:

```bash
./pytest.sh
```

## Lint/Format

```bash
./black_all.sh
```
