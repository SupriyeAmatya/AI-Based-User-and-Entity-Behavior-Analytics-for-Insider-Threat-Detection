"""Tests for the feature-group ablation (S22). Run: python -m pytest tests"""
import json

import pandas as pd
import pytest

from src import ablation
from src.features import feature_columns
from src.synthetic import make_synthetic_features

# The 73 model inputs of features_v1.parquet (frozen Nov 8, TEAM_PLAN 2.5.9).
V1_INPUTS = [
    "f_logon_count", "f_logoff_count", "f_first_logon_hour", "f_last_logoff_hour", "f_n_pcs",
    "f_logon_other_pc", "f_afterhours_logon", "f_work_duration", "f_usb_connect", "f_usb_afterhours",
    "f_usb_n_pcs", "f_usb_duration", "f_file_copy", "f_file_doc", "f_file_exe", "f_file_zip",
    "f_file_img", "f_file_afterhours", "f_email_sent", "f_email_recipients", "f_email_external",
    "f_email_attach", "f_email_external_attach", "f_email_size", "f_email_bcc", "f_email_afterhours",
    "f_http_count", "f_http_domains", "f_http_afterhours", "f_http_job", "f_http_leak", "f_http_cloud",
    "f_http_hack", "f_afterhours_events", "f_afterhours_ratio", "f_weekend", "f_ctx_O", "f_ctx_C",
    "f_ctx_E", "f_ctx_A", "f_ctx_N",
    *[f"{p}_{x}" for p in ("z_user", "z_peer") for x in (
        "logon_count", "first_logon_hour", "work_duration", "afterhours_events", "usb_connect",
        "file_copy", "email_external", "email_recipients", "http_count", "http_job", "http_leak",
        "http_cloud", "http_hack", "logon_other_pc")],
    "new_usb_user", "new_pc", "new_leak_site", "new_afterhours",
]
GROUP_SIZES = {"logon": 16, "time": 7, "usb": 7, "file": 8, "email": 12, "http": 18, "context": 5}


def test_v1_input_list_matches_the_real_table():
    """Guards the freeze: if v1 gains or loses a column, the ablation groups must be revisited."""
    from src.config import PROCESSED_DIR
    path = PROCESSED_DIR / "features_v1.parquet"
    if not path.exists():
        pytest.skip("features_v1.parquet not present")
    import pyarrow.parquet as pq
    from src.features import FEATURE_PREFIXES
    real = [c for c in pq.read_schema(path).names if c.startswith(FEATURE_PREFIXES)]
    assert real == V1_INPUTS


def test_every_v1_input_has_a_group():
    groups = pd.Series({c: ablation.feature_group(c) for c in V1_INPUTS})
    assert len(V1_INPUTS) == 73 and groups.value_counts().to_dict() == GROUP_SIZES
    assert groups["z_user_usb_connect"] == "usb" and groups["new_leak_site"] == "http"
    assert groups["new_pc"] == "logon" and groups["new_afterhours"] == "time"
    assert groups["f_ctx_O"] == "context" and groups["f_afterhours_ratio"] == "time"
    assert groups["z_user_first_logon_hour"] == "logon" and groups["f_logon_other_pc"] == "logon"
    with pytest.raises(ValueError):
        ablation.feature_group("label")


def test_feature_sets():
    sets = ablation.feature_sets(V1_INPUTS)
    raw = [c for c in V1_INPUTS if c.startswith("f_")]
    assert sets["a_raw"] == raw and sets["c_full"] == V1_INPUTS
    assert set(sets["b_raw_z_user"]) == set(raw) | {c for c in V1_INPUTS if c.startswith("z_user_")}
    assert {f"d_full_minus_{g}" for g in ablation.GROUPS} <= set(sets) and len(sets) == 10
    for g, size in GROUP_SIZES.items():
        dropped = set(V1_INPUTS) - set(sets[f"d_full_minus_{g}"])
        assert len(dropped) == size and all(ablation.feature_group(c) == g for c in dropped)


def test_run_ablation_on_synthetic(tmp_path, monkeypatch):
    monkeypatch.setattr(ablation, "TABLES_DIR", tmp_path)
    df = make_synthetic_features()
    table = ablation.run_ablation(df)
    # synthetic data has no context features: 3 + 6 feature sets, each for 2 models
    assert len(table) == 18 and set(table["model"]) == set(ablation.MODELS)
    sets = ablation.feature_sets(feature_columns(df))
    assert (table["n_features"] == table["feature_set"].map(lambda s: len(sets[s]))).all()
    for col in ("test_pr_auc", "recall_top_1pct", "recall_best_f1"):
        assert table[col].between(0, 1).all(), col
    assert (table.loc[table["feature_set"] == "c_full", "delta_pr_auc_vs_full"] == 0).all()
    params = table.set_index("model")["params"].map(json.loads)
    assert "scale_pos_weight" in params["xgboost"].iloc[0] and "n_estimators" in params["iforest"].iloc[0]
    assert table["commit"].nunique() == 1
    assert len(pd.read_csv(tmp_path / ablation.TABLE)) == 18


def test_unknown_model_is_refused():
    with pytest.raises(ValueError, match="unknown model"):
        ablation.run_ablation(make_synthetic_features(), models=("lstm",), save=False)
