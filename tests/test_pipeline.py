"""Tests for the UEBA prototype (A11 pipeline, A12 alert reasons). Run: python -m pytest tests"""
import pandas as pd
import pytest

from src import pipeline
from src.synthetic import make_synthetic_features


@pytest.fixture
def features_file(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "MODELS_DIR", tmp_path / "models")
    monkeypatch.setattr(pipeline, "TABLES_DIR", tmp_path / "tables")
    monkeypatch.setattr(pipeline, "ROOT", tmp_path)
    path = tmp_path / "features_synthetic.parquet"
    make_synthetic_features().to_parquet(path, index=False)
    return path


@pytest.mark.parametrize("model, params", [("iforest", None), ("autoencoder", {"epochs": 5})])
def test_pipeline_ranks_users_with_three_reasons(features_file, tmp_path, model, params):
    table, risk = pipeline.run(features_file, model, top=10, params=params, verbose=False)
    assert len(table) == 10 and table["rank"].tolist() == list(range(1, 11))
    assert table["peak_risk"].is_monotonic_decreasing
    assert "label" not in table.columns and "scenario" not in table.columns   # analyst view
    # 1 to 3 reasons each: a z-score below MIN_REASON_Z is not a reason (review of #57)
    assert table["reasons"].str.len().gt(0).all() and table["reasons"].str.count("; ").le(2).all()
    saved = pd.read_csv(tmp_path / "tables" / pipeline.OUTPUT)
    assert saved["user"].tolist() == table["user"].tolist()
    assert pipeline.model_path(model, features_file).exists()
    # The 3 synthetic insiders with malicious days in the test period all make the top 10.
    test_insiders = set(risk.loc[(risk["label"] == 1) & (risk["split"] == "test"), "user"])
    assert len(test_insiders) == 3 and test_insiders <= set(table["user"])


def test_saved_model_is_reused_and_retrained_on_new_columns(features_file, capsys):
    pipeline.run(features_file, "iforest", top=5)
    assert "trained and saved" in capsys.readouterr().out
    pipeline.run(features_file, "iforest", top=5)
    assert "loaded" in capsys.readouterr().out
    df = pd.read_parquet(features_file).drop(columns=["z_user_http_job"])
    df.to_parquet(features_file, index=False)
    pipeline.run(features_file, "iforest", top=5)
    assert "trained and saved" in capsys.readouterr().out         # other columns -> retrain


def test_rank_for_one_day(features_file):
    df = pd.read_parquet(features_file)
    day = df.loc[(df["split"] == "test") & (df["label"] == 1), "date"].max()
    table, _ = pipeline.run(features_file, "iforest", top=5, date=day, verbose=False)
    assert len(table) == 5 and table["reasons"].str.len().gt(0).all()


def test_reasons_skip_values_at_baseline_and_empty_email_size():
    # review of #57: a large autoencoder residual on a feature that sits at its baseline (z = 0),
    # or on the mean email size of a day with no email, is not a reason
    cols = ["z_user_http_job", "z_peer_http_job", "z_user_usb_connect", "f_email_size",
            "f_file_copy", "z_user_logon_count"]
    df = pd.DataFrame([[0.0, -0.4, 6.2, 0.0, 37.0, float("nan")],
                       [1.0, 0.99, -3.0, 2048.0, 0.0, 0.2]], columns=cols)
    contrib = pd.DataFrame([[9.0, 8.0, 5.0, 7.0, 4.0, 6.0],
                            [9.0, 8.0, 5.0, 7.0, 4.0, 6.0]], columns=cols)
    reasons = pipeline.alert_reasons(contrib, df)
    assert reasons[0] == "USB connects 6.2σ above own baseline; 37 files copied"
    assert reasons[1] == ("job-site visits 1.0σ above own baseline; mean email size (bytes): 2048; "
                          "USB connects 3.0σ below own baseline")
    assert pipeline.MIN_REASON_Z > 0
    assert pipeline.describe("z_user_http_competitor", 3.7) == \
        "competitor-site visits 3.7σ above own baseline"


def test_describe_reasons():
    assert pipeline.describe("z_user_usb_connect", 6.24) == "USB connects 6.2σ above own baseline"
    assert pipeline.describe("z_peer_http_job", -2.0) == "job-site visits 2.0σ below peers"
    assert pipeline.describe("f_file_copy", 37) == "37 files copied"
    assert pipeline.describe("new_leak_site", 1) == "first-ever leak or file-sharing site visit"
    assert pipeline.describe("f_first_logon_hour", 3.5) == "first logon hour: 3.5"
