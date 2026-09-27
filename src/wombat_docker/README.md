# Mellow Validator Blueprint (Wombat Docker)

This directory is a working example of a mellow validator application.
It is designed to run either:

1. Locally with Python
2. In Docker with mounted data directories

Use this as a template when creating future validator-style applications.

## Purpose

The validator reads collected JSON files from a fresh directory, validates each
file against schema and business rules, records accepted files in PostgreSQL
load-log storage, then moves files to success or failure directories.

## Components

### 1) Application Entrypoint

File: manatee_app.py

- Builds database connectivity from environment variables.
- Configures SQLAlchemy engine options (connection timeout, statement timeout,
  pool pre-ping).
- Routes execution by stuntbox mode.
- Current mode: validator.

### 2) Validator Engine

File: validator.py

- Iterates files in the configured fresh directory.
- Uses JsonHelper to validate file structure and content.
- Enforces idempotency by checking the load-log table for previously processed
  file names.
- Resolves geo location references by site name before insert.
- On success: inserts load-log row and moves file to success directory.
- On failure: moves file to failure directory.
- Tracks run counters for success and failure outcomes.

### 3) JSON Schema and File Rules

File: ../helper/json_helper.py

- Defines JSON schema for payload sections:
  equipment, geoLoc, job, receiver, timeStamp, crateName, fileName, version,
  observations.
- Enforces required fields and disallows additional properties.
- Verifies business checks in validator.py:
  payload fileName must match actual file name,
  payload version must be 1,
  payload job.project must be manatee-v1.

### 4) Persistence Layer

Files: ../helper/postgres.py and ../helper/sql_table.py

- Implements data access methods used by the validator.
- Load-log fields currently include:
  crate_name, epoch_seconds, file_name, geo_loc_id, host_name, load_time,
  obs_quantity, obs_time, site_name, source_file_name, task.
- Primary idempotency key in current implementation is file_name lookup.

## Runtime Configuration

The validator behavior is controlled by environment variables.

### Required/Supported Variables

1. DB_CONN
2. PG_CONNECT_TIMEOUT (default 5)
3. PG_STATEMENT_TIMEOUT_MS (default 5000)
4. FRESH_DIR (default /var/wombat/fresh/manatee)
5. SUCCESS_DIR (default /var/wombat/manatee/success)
6. FAILURE_DIR (default /var/wombat/failure)
7. stuntbox (default validator)

## Local Run Pattern

Typical local workflow:

1. Create/activate virtualenv
2. Install requirements from requirements.txt
3. Export DB and directory environment variables
4. Run python manatee_app.py

Example:

```bash
cd src/wombat_docker
source venv/bin/activate
pip install -r requirements.txt

export DB_CONN="postgresql+psycopg2://manatee_client:batabat@localhost:5432/manatee"
export FRESH_DIR="/var/wombat/fresh/manatee"
export SUCCESS_DIR="/var/wombat/manatee/success"
export FAILURE_DIR="/var/wombat/failure"
export stuntbox="validator"

python manatee_app.py
```

## Testing With Pytest

Pytest tests for this validator live in the same directory as manatee_app.py
and validator.py.

Run tests from src/wombat_docker/pytest.sh

## Docker Run Pattern

The Docker image includes manatee_app.py, validator.py, and helper modules.
Data paths are expected under /mnt/wombat and should be mounted from host
storage.

Build:

```bash
docker build -f src/wombat_docker/Dockerfile -t manatee:latest src/
```

Run:

```bash
docker run \
  -e stuntbox=validator \
  -e DB_CONN="postgresql+psycopg2://manatee_client:batabat@172.17.0.1:5432/manatee" \
  -v /var/wombat:/mnt/wombat \
  --name manatee \
  manatee:latest
```

## Reuse Checklist For Future Applications

When creating a new validator application with the same features:

1. Keep the same app split:
   small entrypoint + validator service + helper modules.
2. Keep all runtime behavior configurable by environment variables.
3. Define schema and business validation in one helper module.
4. Keep idempotency checks in persistence layer before accepting files.
5. Keep deterministic file movement semantics (fresh -> success/failure).
6. Keep observability logs at each transition point.
7. Add a Dockerfile that mirrors local defaults so local and container behavior
   match.

## Extension Points

Future validator projects can extend this template by:

1. Adding new stuntbox modes in manatee_app.py.
2. Adding new database methods in helper/postgres.py for richer audit/reporting.
3. Expanding schema in helper/json_helper.py for new observation formats.
4. Replacing os.rename moves with archive+copy or object-storage writes.
5. Adding retry queues and dead-letter handling for transient failures.

## Notes and Known Gaps

1. json_helper.py currently pins version/project business rules to version=1 and
   project=manatee-v1.

Treat these as intentional constraints for this template unless your next
application requires different policy.
