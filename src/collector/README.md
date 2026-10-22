## Collector Blueprint For Manatee

This collector discovers completed listener output files and moves them into the fresh-ingest directory for validation.

### Core Design

1. Uses an abstract collector interface (`get_observations`, `execute`) with a concrete `ManateeCollector` implementation.
2. Discovers listener output files in `rawDir` using the host/hour manatee filename pattern.
3. Skips currently active hour files so listener can continue appending safely.
4. Moves completed `.json` and `.raw` files into `freshDir` unchanged.

### Execution Flow

1. Load YAML config (`config.yaml` by default).
2. Instantiate typed model objects from config fields.
3. Derive current-hour manatee file prefix from receiver hostname and UTC hour.
4. Discover candidates in `rawDir` matching the manatee file prefix pattern.
5. Skip files from the active hour.
6. Move completed source files (`.json` and `.raw`) into `freshDir`.

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

`listener.py` now emits validator-ready JSON payloads directly. `collector.py` does not rewrite payloads.

### Integration Pattern

1. `bootboy.py` generates `config.yaml` from host/admin metadata.
2. `listener.py` writes decode output files into the raw area.
3. `collector.py` moves completed files to `freshDir`.
4. `collector.sh` activates the venv and executes `collector.py` on schedule.

### Testing With Pytest

Pytest tests for this collector live in the same directory as `collector.py`.

Run tests from `src/collector/pytest.sh`.

### Notes

1. BootBoy behavior (service start plus once-daily schedule) is intentional for manatee operations.
2. Listener payloads retain `sourceFileName` for source-file traceability in downstream processing.
