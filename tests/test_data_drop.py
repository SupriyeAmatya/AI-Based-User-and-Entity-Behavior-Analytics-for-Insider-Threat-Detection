"""Tests for the data-drop script (S4/S20, TEAM_PLAN 2.5.12). Run: python -m pytest tests"""
import importlib.util
import zipfile
from pathlib import Path

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


def test_make_zips_every_file_with_checksums(tmp_path):
    _fake_data(tmp_path)
    out = data_drop.make(tmp_path)
    assert out == tmp_path / "data" / "ueba_data_v1.zip"
    with zipfile.ZipFile(out) as z:
        names = set(z.namelist())
    assert names == set(data_drop.FILES) | {data_drop.CHECKSUMS, data_drop.INFO}
    assert not any("http.parquet" in n or n.startswith("data/raw") for n in names)
    info = (tmp_path / data_drop.INFO).read_text(encoding="utf-8")
    assert "WORK_START_HOUR" in info and "commit:" in info


def test_verify_after_unzip_and_detects_changes(tmp_path):
    src, dst = tmp_path / "laptop_supriye", tmp_path / "laptop_arva"
    _fake_data(src)
    with zipfile.ZipFile(data_drop.make(src)) as z:
        z.extractall(dst)
    assert data_drop.verify(dst) == []
    (dst / "data/processed/features_v1.parquet").write_bytes(b"edited")
    (dst / "data/parquet/email.parquet").unlink()
    assert sorted(data_drop.verify(dst)) == ["CHANGED  data/processed/features_v1.parquet",
                                             "MISSING  data/parquet/email.parquet"]
    assert data_drop.verify(tmp_path / "empty")[0].startswith("data/CHECKSUMS.txt not found")


def test_make_stops_when_a_file_is_missing(tmp_path):
    _fake_data(tmp_path)
    (tmp_path / "data/processed/features_v1.parquet").unlink()
    with pytest.raises(FileNotFoundError, match="features_v1.parquet"):
        data_drop.make(tmp_path)
