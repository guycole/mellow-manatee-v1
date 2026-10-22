import json

from collector import ManateeCollector, TimeStamp
from listener import Listener


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


def test_execute_moves_listener_payload_to_fresh(tmp_path) -> None:
    raw_dir = tmp_path / "raw"
    fresh_dir = tmp_path / "fresh"
    raw_dir.mkdir()
    fresh_dir.mkdir()

    source_name = "manatee_demo-host_20000101_00.json"
    source_path = raw_dir / source_name
    source_payload = (
        '{"crate":"demo-crate","fileName":"manatee_demo-host_20000101_00.json",'
        '"version":1,"equipment":{"antenna":"dipole","receiverId":7,'
        '"receiverType":"rtl","hostName":"demo-host","hostType":"laptop"},'
        '"geoLoc":{"altitude":100.0,"latitude":42.0,"longitude":-71.0,'
        '"siteName":"demo-site"},'
        '"job":{"mode":"rtl_ais","project":"manatee-v1","task":"manatee-v1-ra"},'
        '"sourceFileName":"manatee_demo-host_20000101_00.raw",'
        '"timeStamp":{"epochSeconds":0,"iso8601":"1970-01-01T00:00:00+00:00"},'
        '"observations":[{"name":"obs1"}]}'
    )
    source_path.write_text(source_payload, encoding="utf-8")

    raw_blob_name = "manatee_demo-host_20000101_00.raw"
    raw_blob_path = raw_dir / raw_blob_name
    raw_blob_path.write_bytes(b"raw-data")

    collector = ManateeCollector(_config(str(raw_dir), str(fresh_dir)))

    result = collector.execute()

    assert result == 0

    output_path = fresh_dir / source_name
    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8") == source_payload
    assert (fresh_dir / raw_blob_name).exists()


def test_listener_writes_validator_ready_payload(tmp_path, monkeypatch) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    config = _config(str(raw_dir), str(tmp_path / "fresh"))
    listener = Listener(config)

    monkeypatch.setattr("listener.time.time", lambda: 0)
    monkeypatch.setattr("listener.uuid.uuid4", lambda: "00000000-0000-0000-0000-000000000001")

    class _Decoded:
        def asdict(self):
            return {"mmsi": 123}

    monkeypatch.setattr("listener.decode", lambda *_args: _Decoded())

    base_file_name = f"{raw_dir}/manatee_demo-host_19700101_00"
    data = b"!AIVDM,1,1,,A,13aG?P0000PD;88MD5MTDwwj0D0u,0*7D\\n"

    result = listener.write_decode_file(base_file_name, data)

    assert result is True
    payload_path = raw_dir / "manatee_demo-host_19700101_00.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    assert payload["crate"] == "demo-crate"
    assert payload["fileName"] == "manatee_demo-host_19700101_00.json"
    assert payload["version"] == 1
    assert payload["job"]["project"] == "manatee-v1"
    assert payload["sourceFileName"] == "manatee_demo-host_19700101_00.raw"
    assert payload["timeStamp"]["epochSeconds"] == 0
    assert payload["observations"] == [
        {"mmsi": 123, "epochSeconds": 0, "uuid": "00000000-0000-0000-0000-000000000001"}
    ]
