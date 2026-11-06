"""Tests for the data-drop script (S4/S20, TEAM_PLAN 2.5.12). Run: python -m pytest tests"""
import importlib.util
import zipfile
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

spec = importlib.util.spec_from_file_location(
    "data_drop", Path(__file__).resolve().parents[1] / "scripts" / "data_drop.py")
data_drop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_drop)


def _fake_data(root: Path):
    for i, f in enumerate(data_drop.FILES):
        path = root / f
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"content {i}".encode())


def _web_cache(root: Path, stamp):
    """A real (tiny) web-log cache, with or without a working-hours stamp."""
    table = pa.Table.from_pandas(pd.DataFrame({"domain": ["x.com"], "visits": [1]}), preserve_index=False)
    if stamp is not None:
        table = table.replace_schema_metadata({**table.schema.metadata, b"work_hours": stamp.encode()})
    pq.write_table(table, root / data_drop.WEB_CACHE)


def test_file_list_matches_the_plan():
    assert len(data_drop.FILES) == 10 and data_drop.WEB_CACHE in data_drop.FILES
    assert all(f.startswith(("data/processed/", "data/parquet/")) for f in data_drop.FILES)
    assert not any(f.endswith("http.parquet") for f in data_drop.FILES)


def test_make_zips_every_file_with_checksums(tmp_path):
    _fake_data(tmp_path)
    out = data_drop.make(tmp_path, check_cache=False)
    assert out == tmp_path / "data" / "ueba_data_v1.zip"
    with zipfile.ZipFile(out) as z:
        names = set(z.namelist())
    assert names == set(data_drop.FILES) | {data_drop.CHECKSUMS, data_drop.INFO}
    assert not any(n.startswith("data/raw") for n in names)
    info = (tmp_path / data_drop.INFO).read_text(encoding="utf-8")
    assert "WORK_START_HOUR = " in info and "commit:" in info and "HTTP_CATEGORIES = " in info


def test_make_refuses_a_web_cache_built_with_other_hours(tmp_path):
    _fake_data(tmp_path)
    for stamp in (None, "6-20"):
        _web_cache(tmp_path, stamp)
        with pytest.raises(ValueError, match="python -m src.features v1"):
            data_drop.make(tmp_path)
    from src.features import work_hours_stamp
    _web_cache(tmp_path, work_hours_stamp())
    assert data_drop.make(tmp_path).exists()


def test_verify_after_unzip_and_detects_changes(tmp_path):
    src, dst = tmp_path / "laptop_supriye", tmp_path / "laptop_arva"
    _fake_data(src)
    with zipfile.ZipFile(data_drop.make(src, check_cache=False)) as z:
        z.extractall(dst)
    assert data_drop.verify(dst) == [] and data_drop.decision_warnings(dst) == []
    (dst / "data/processed/features_v1.parquet").write_bytes(b"edited")
    (dst / "data/parquet/email.parquet").unlink()
    assert sorted(data_drop.verify(dst)) == ["CHANGED  data/processed/features_v1.parquet",
                                             "MISSING  data/parquet/email.parquet"]
    assert data_drop.verify(tmp_path / "empty")[0].startswith("data/CHECKSUMS.txt not found")


def test_verify_warns_when_the_drop_used_other_decisions(tmp_path):
    _fake_data(tmp_path)
    data_drop.make(tmp_path, check_cache=False)
    info = tmp_path / data_drop.INFO
    info.write_text(info.read_text(encoding="utf-8").replace("WORK_END_HOUR = ", "WORK_END_HOUR = 99"),
                    encoding="utf-8")
    warnings = data_drop.decision_warnings(tmp_path)
    assert len(warnings) == 1 and "WORK_END_HOUR = 99" in warnings[0]


def test_make_stops_when_a_file_is_missing(tmp_path):
    _fake_data(tmp_path)
    (tmp_path / "data/processed/features_v1.parquet").unlink()
    with pytest.raises(FileNotFoundError, match="features_v1.parquet"):
        data_drop.make(tmp_path)


def test_cli_exit_codes(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(data_drop, "ROOT", tmp_path)
    assert data_drop.main(["make"]) == 1 and "Not built" in capsys.readouterr().out   # no data
    assert data_drop.main(["verify"]) == 1                                             # no drop
    _fake_data(tmp_path)
    data_drop.make(tmp_path, check_cache=False)
    assert data_drop.main(["verify"]) == 0 and "OK" in capsys.readouterr().out
    assert data_drop.main([]) == 0
