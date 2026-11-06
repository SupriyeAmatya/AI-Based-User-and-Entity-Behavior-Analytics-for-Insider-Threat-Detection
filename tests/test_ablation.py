"""Tests for the feature-group ablation (S22). Run: python -m pytest tests"""
import pandas as pd
import pytest

from src import ablation
from src.synthetic import make_synthetic_features


@pytest.fixture(scope="module")
def v1_inputs():
    """Every model-input column of feature table v1, if it is present; else a fixed v1 list."""
    from src.config import PROCESSED_DIR
    path = PROCESSED_DIR / "features_v1.parquet"
    if path.exists():
        import pyarrow.parquet as pq
        from src.features import FEATURE_PREFIXES
        return [c for c in pq.read_schema(path).names if c.startswith(FEATURE_PREFIXES)]
    return ["f_logon_count", "f_logoff_count", "f_first_logon_hour", "f_last_logoff_hour", "f_n_pcs",
            "f_logon_other_pc", "f_afterhours_logon", "f_work_duration", "f_usb_connect",
            "f_file_copy", "f_email_sent", "f_http_count", "f_http_leak", "f_afterhours_events",
            "f_afterhours_ratio", "f_weekend", "f_ctx_O", "z_user_usb_connect", "z_peer_http_leak",
            "z_user_first_logon_hour", "new_usb_user", "new_pc", "new_leak_site", "new_afterhours"]


def test_every_input_has_a_group(v1_inputs):
    groups = {c: ablation.feature_group(c) for c in v1_inputs}
    assert set(groups.values()) == set(ablation.GROUPS)
    assert groups["z_user_usb_connect"] == "usb" and groups["new_leak_site"] == "http"
    assert groups["new_pc"] == "logon" and groups["new_afterhours"] == "time"
    assert groups["f_ctx_O"] == "context" and groups["f_afterhours_ratio"] == "time"
    assert groups["z_user_first_logon_hour"] == "logon" and groups["f_logon_other_pc"] == "logon"
    with pytest.raises(ValueError):
        ablation.feature_group("label")


def test_feature_sets(v1_inputs):
    sets = ablation.feature_sets(v1_inputs)
    raw = [c for c in v1_inputs if c.startswith("f_")]
    assert sets["a_raw"] == raw and sets["c_full"] == list(v1_inputs)
    assert set(sets["b_raw_z_user"]) == set(raw) | {c for c in v1_inputs if c.startswith("z_user_")}
    assert {f"d_full_minus_{g}" for g in ablation.GROUPS} <= set(sets) and len(sets) == 10
    for g in ablation.GROUPS:
        dropped = set(v1_inputs) - set(sets[f"d_full_minus_{g}"])
        assert dropped and all(ablation.feature_group(c) == g for c in dropped)


def test_run_ablation_on_synthetic(tmp_path, monkeypatch):
    monkeypatch.setattr(ablation, "TABLES_DIR", tmp_path)
    table = ablation.run_ablation(make_synthetic_features())
    # synthetic data has no context features: 3 + 6 feature sets, each for 2 models
    assert len(table) == 18 and set(table["model"]) == set(ablation.MODELS)
    assert table["test_pr_auc"].between(0, 1).all() and table["recall_top_1pct"].between(0, 1).all()
    assert (table.loc[table["feature_set"] == "c_full", "delta_pr_auc_vs_full"] == 0).all()
    saved = pd.read_csv(tmp_path / ablation.TABLE)
    assert len(saved) == 18
