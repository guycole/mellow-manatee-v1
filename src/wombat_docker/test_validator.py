import logging

from validator import ManateeValidator


class FakeGeoLoc:
    def __init__(self, geo_id: int):
        self.id = geo_id


class FakePostgres:
    def __init__(self):
        self.selected = None
        self.inserted = []
        self.daily_scores = []
        self.geo_locs = [FakeGeoLoc(42)]

    def load_log_select_by_file_name(self, _file_name):
        return self.selected

    def geo_loc_select_by_site(self, _site_name):
        return self.geo_locs

    def load_log_insert(self, load_log):
        self.inserted.append(load_log)

    def daily_score_insert_or_update(self, daily_score):
        self.daily_scores.append(daily_score)


def _validator() -> tuple[ManateeValidator, FakePostgres]:
    postgres = FakePostgres()
    validator = ManateeValidator(logging.getLogger("test"), postgres)
    return validator, postgres


def test_load_log_test_inserts_when_not_previously_processed() -> None:
    validator, postgres = _validator()
    validator.json_helper.raw_json = {
        "crate": "crate-a",
        "timeStamp": {"epochSeconds": 1, "iso8601": "1970-01-01T00:00:01+00:00"},
        "equipment": {"hostName": "host-a"},
        "job": {"mode": "default", "task": "task-a", "project": "manatee-v1"},
        "geoLoc": {"siteName": "site-a"},
        "sourceFileName": "source-a.json",
        "observations": [],
    }

    result = validator.load_log_test("abc.json")

    assert result is True
    assert len(postgres.inserted) == 1
    assert postgres.inserted[0]["file_name"] == "abc.json"
    assert postgres.inserted[0]["epoch_seconds"] == 1
    assert postgres.inserted[0]["geo_loc_id"] == 42
    assert postgres.inserted[0]["obs_quantity"] == 0
    assert postgres.inserted[0]["source_file_name"] == "source-a.json"
    assert len(postgres.daily_scores) == 1


def test_file_processor_success_path(monkeypatch) -> None:
    validator, _postgres = _validator()
    monkeypatch.setattr("validator.os.path.isfile", lambda _name: True)
    monkeypatch.setattr("validator.os.path.getsize", lambda _name: 10)
    monkeypatch.setattr(
        validator.json_helper, "json_file_reader", lambda _name, _flag: True
    )
    validator.json_helper.raw_json = {
        "fileName": "ok.json",
        "version": 1,
        "job": {"project": "manatee-v1"},
    }
    monkeypatch.setattr(validator, "load_log_test", lambda _name: True)

    calls = {"success": 0, "failure": 0}
    monkeypatch.setattr(
        validator,
        "file_success",
        lambda _name: calls.__setitem__("success", calls["success"] + 1),
    )
    monkeypatch.setattr(
        validator,
        "file_failure",
        lambda _name: calls.__setitem__("failure", calls["failure"] + 1),
    )

    result = validator.file_processor("ok.json")

    assert result is True
    assert calls["success"] == 1
    assert calls["failure"] == 0


def test_execute_processes_non_raw_targets(monkeypatch) -> None:
    validator, _postgres = _validator()

    monkeypatch.setattr("validator.os.chdir", lambda _path: None)
    monkeypatch.setattr(
        "validator.os.listdir", lambda _path: ["b.json", "a.raw", "a.json"]
    )

    processed = []
    skipped_raw = []
    monkeypatch.setattr(
        validator, "file_processor", lambda name: processed.append(name) or True
    )
    monkeypatch.setattr(
        validator, "file_success", lambda name: skipped_raw.append(name)
    )

    result = validator.execute()

    assert result == 0
    assert processed == ["a.json", "b.json"]
    assert skipped_raw == ["a.raw"]
