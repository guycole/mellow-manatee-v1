import json
import uuid

from collector import ManateeCollector, TimeStamp


def _config(raw_dir: str, fresh_dir: str) -> dict[str, object]:
    return {
        "crateName": "demo-crate",
        "rawDir": raw_dir,
        "freshDir": fresh_dir,
        "equipment": {
            "hostName": "demo-host",
            "hostType": "laptop",
        },
        "geoLoc": {
            "altitude": 100.0,
            "latitude": 42.0,
            "longitude": -71.0,
            "siteName": "demo-site",
        },
        "receiver": {
            "antenna": "dipole",
            "mode": "rtl_ais",
            "receiverId": 7,
            "task": "manatee-v1-ra",
            "type": "rtl",
        },
    }


def test_timestamp_syncs_iso8601_from_epoch_seconds() -> None:
    stamp = TimeStamp(epoch_seconds=0)

    assert stamp.iso8601 == "1970-01-01T00:00:00+00:00"


def test_collector_derives_job_from_receiver_task(tmp_path) -> None:
    raw_dir = tmp_path / "raw"
    fresh_dir = tmp_path / "fresh"
    raw_dir.mkdir()
    fresh_dir.mkdir()

    collector = ManateeCollector(_config(str(raw_dir), str(fresh_dir)))

    assert collector.job.mode == "rtl_ais"
    assert collector.job.project == "manatee-v1-ra"
    assert collector.job.task == "manatee-v1-ra"


def test_execute_writes_expected_payload_file(tmp_path, monkeypatch) -> None:
    fixed_uuid = uuid.UUID("5cc9fa9d-5065-400e-b578-76633bdd3699")
    monkeypatch.setattr("collector.uuid.uuid4", lambda: fixed_uuid)

    raw_dir = tmp_path / "raw"
    fresh_dir = tmp_path / "fresh"
    raw_dir.mkdir()
    fresh_dir.mkdir()

    source_name = "manatee_demo-host_20000101_00.json"
    source_path = raw_dir / source_name
    source_path.write_text('[{"name": "obs1"}]\n', encoding="utf-8")

    collector = ManateeCollector(_config(str(raw_dir), str(fresh_dir)))
    collector.time_stamp = TimeStamp(epoch_seconds=0)

    result = collector.execute()

    assert result == 0

    output_path = fresh_dir / f"{fixed_uuid}.json"
    assert output_path.exists()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["crateName"] == "demo-crate"
    assert payload["fileName"] == f"{fixed_uuid}.json"
    assert payload["job"]["project"] == "manatee-v1-ra"
    assert payload["receiver"]["task"] == "manatee-v1-ra"
    assert payload["source_file_name"] == source_name
    assert payload["timeStamp"]["epochSeconds"] == 0
    assert payload["timeStamp"]["iso8601"] == "1970-01-01T00:00:00+00:00"
    assert payload["observations"] == [{"name": "obs1"}]

    moved_source_path = fresh_dir / source_name
    assert moved_source_path.exists()
