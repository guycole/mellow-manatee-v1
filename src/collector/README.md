## Collector Blueprint For Manatee

This collector discovers completed AIS decode files, wraps their observations in a typed payload, and writes a timestamped JSON artifact into the fresh-ingest directory. The design stays close to the slug collector blueprint while preserving manatee-specific ingest behavior.

### Core Design

1. Uses Pydantic models to define payload sections: crateName, fileName, equipment, geoLoc, job, receiver, source_file_name, timeStamp, and observations.
2. Generates UTC timestamps from epoch seconds automatically.
3. Uses an abstract collector interface (`get_observations`, `execute`) with a concrete `ManateeCollector` implementation.
4. Builds output file names with UUID values to avoid collisions.
5. Reads newline-delimited JSON arrays from discovered raw decode files.
6. Writes one wrapped payload JSON file per discovered source JSON file.

### Execution Flow

1. Load YAML config (`config.yaml` by default).
2. Instantiate typed model objects from config fields.
3. Derive job metadata (`mode`, `project`, `task`) from receiver/task context.
4. Discover candidates in `rawDir` matching the manatee file prefix pattern.
5. Parse observations from source `.json` files.
6. Build the final manatee payload (including `source_file_name`).
7. Serialize formatted JSON to `freshDir/<uuid>.json`.
8. Move processed source files (`.json` and `.raw`) into `freshDir`.

### Required Configuration Contract

The collector expects these keys in `config.yaml`:

1. `crateName`
2. `rawDir`
3. `freshDir`
4. `equipment.hostName`
5. `equipment.hostType`
6. `geoLoc.altitude`
7. `geoLoc.latitude`
8. `geoLoc.longitude`
9. `geoLoc.siteName`
10. `receiver.antenna`
11. `receiver.mode`
12. `receiver.receiverId`
13. `receiver.task`
14. `receiver.type`

### Output Payload Contract

Each emitted wrapper JSON file contains:

1. `crateName`
2. `fileName`
3. `version`
4. `equipment`
5. `geoLoc`
6. `job`
7. `receiver`
8. `source_file_name`
9. `timeStamp` (`epochSeconds`, `iso8601`)
10. `observations`

### Integration Pattern

1. `bootboy.py` generates `config.yaml` from host/admin metadata.
2. `listener.py` writes decode output files into the raw area.
3. `collector.py` wraps and moves completed files to `freshDir`.
4. `collector.sh` activates the venv and executes `collector.py` on schedule.

### Testing With Pytest

Pytest tests for this collector live in the same directory as `collector.py`.

Run tests from `src/collector/pytest.sh`.

### Notes

1. BootBoy behavior (service start plus once-daily schedule) is intentional for manatee operations.
2. `source_file_name` is retained to preserve source-file traceability in downstream processing.
