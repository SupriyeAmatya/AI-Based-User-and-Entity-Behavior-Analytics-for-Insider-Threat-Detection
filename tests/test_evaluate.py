"""Tests for src/evaluate.py. Run from the repo root: python -m pytest tests"""
import math

import numpy as np
import pandas as pd
import pytest

from src import evaluate as ev


def test_threshold_metrics_hand_example():
    # 10 user-days, 3 malicious. Threshold 0.5 flags the four scores >= 0.5:
    # 0.9 (mal), 0.8 (mal), 0.7 (normal), 0.6 (normal) -> TP=2, FP=2; 0.3 is a missed malicious -> FN=1; TN=5
    y = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
    s = [0.9, 0.8, 0.3, 0.7, 0.6, 0.2, 0.1, 0.05, 0.4, 0.0]
    m = ev.threshold_metrics(y, s, 0.5)
    assert (m["tp"], m["fp"], m["tn"], m["fn"]) == (2, 2, 5, 1)
    assert m["accuracy"] == pytest.approx(7 / 10)
    assert m["precision"] == pytest.approx(2 / 4)
    assert m["recall"] == pytest.approx(2 / 3)
    assert m["f1"] == pytest.approx(2 * 0.5 * (2 / 3) / (0.5 + 2 / 3))
    assert m["fpr"] == pytest.approx(2 / 7)
    assert m["fnr"] == pytest.approx(1 / 3)


def test_threshold_metrics_flags_nothing_without_crashing():
    m = ev.threshold_metrics([1, 0, 0], [0.1, 0.2, 0.3], 1.0)
    assert m["precision"] == 0 and m["recall"] == 0 and m["f1"] == 0


def test_ranking_metrics_single_class_is_nan():
    r = ev.ranking_metrics([0, 0, 0], [0.1, 0.2, 0.3])
    assert math.isnan(r["roc_auc"]) and math.isnan(r["pr_auc"])


def test_thresholds():
    val = pd.DataFrame({"label": [0, 0, 1, 1], "score": [0.1, 0.2, 0.8, 0.9]})
    assert ev.threshold_best_f1(val) == pytest.approx(0.8)  # flags exactly the two malicious rows
    assert ev.threshold_best_f1(val.assign(label=0)) == float("inf")
    test = pd.DataFrame({"score": np.arange(100)})
    assert (test["score"] >= ev.threshold_top_k(test, 0.01)).sum() == 1


def test_detection_delay_and_user_recall():
    d = pd.to_datetime
    test = pd.DataFrame({
        "user": ["A"] * 4 + ["B"] * 2,
        "date": d(["2011-01-01", "2011-01-03", "2011-01-04", "2011-01-05", "2011-01-03", "2011-01-04"]),
        "label": [0, 1, 1, 0, 1, 0],
        "scenario": [0, 1, 1, 0, 2, 0],
        "score": [0.9, 0.1, 0.8, 0.2, 0.1, 0.1],
    })
    # A: first malicious day Jan 3, first alert on/after it Jan 4 -> 1 day (the Jan 1 alert is earlier, ignored)
    # B: never flagged -> missed
    delay = ev.detection_delay(test, 0.5)
    assert delay["n_insiders"] == 2 and delay["n_missed"] == 1
    assert delay["median_delay_days"] == 1
    assert ev.user_level_recall(test, 0.5) == pytest.approx(0.5)


def test_evaluate_and_compare_on_synthetic(tmp_path, monkeypatch):
    monkeypatch.setattr(ev, "FIGURES_DIR", tmp_path / "figures")
    df = ev.make_synthetic_scores()
    assert len(df) == 10_000
    assert 0.003 < df["label"].mean() < 0.007
    for split in ("train", "val", "test"):
        assert set(df.loc[(df["split"] == split) & (df["label"] == 1), "scenario"]) == {1, 2, 3}

    path = tmp_path / "xgboost.parquet"
    df.to_parquet(path)
    r = ev.evaluate_file(path)
    assert r["model"] == "xgboost"
    assert set(r["operating_points"]) == {"best_f1", "top_1pct"}
    assert set(r["per_scenario"]) == {1, 2, 3}
    assert r["ranking"]["roc_auc"] > 0.8  # positives are shifted by +1.5

    table = ev.compare_files([path])
    assert list(table["operating_point"]) == ["best_f1", "top_1pct"]

    for plot in (ev.plot_roc([path]), ev.plot_pr([path]), ev.plot_confusion(path),
                 ev.plot_score_distribution(path)):
        assert plot is not None
    assert (tmp_path / "figures" / "roc_curves.png").exists()


# ---------------------------------------------------------------- Y17: comparison tables, F5, T8
@pytest.fixture
def two_files(tmp_path, monkeypatch):
    """Two synthetic score files (different seeds) named like real models; outputs go to tmp."""
    monkeypatch.setattr(ev, "FIGURES_DIR", tmp_path / "figures")
    monkeypatch.setattr(ev, "TABLES_DIR", tmp_path / "tables")
    paths = []
    for model, seed in (("iforest", 1), ("xgboost", 2)):
        path = tmp_path / f"{model}.parquet"
        ev.make_synthetic_scores(seed=seed).to_parquet(path)
        paths.append(path)
    return paths


def test_model_comparison_saves_t5(two_files, tmp_path):
    table = ev.model_comparison(two_files)
    assert len(table) == 4 and set(table["model"]) == {"iforest", "xgboost"}
    for column in ("accuracy", "precision", "recall", "f1", "fpr", "fnr", "roc_auc", "pr_auc",
                   "user_recall", "median_delay_days"):
        assert column in table.columns
    assert (tmp_path / "tables" / ev.T5_TABLE).exists()


def test_per_scenario_table_matches_evaluate_file(two_files, tmp_path):
    table = ev.per_scenario_table(two_files)
    assert list(table.columns) == ["model", "scenario", "n_malicious_days", "pr_auc",
                                   "recall_best_f1", "recall_top_1pct"]
    assert len(table) == 6 and set(table["scenario"]) == {1, 2, 3}
    expected = ev.evaluate_file(two_files[1])["per_scenario"][2]
    row = table[(table["model"] == "xgboost") & (table["scenario"] == 2)].iloc[0]
    assert row["pr_auc"] == pytest.approx(expected["pr_auc"])
    assert row["recall_top_1pct"] == pytest.approx(expected["recall_top_1pct"])
    assert (tmp_path / "tables" / ev.PER_SCENARIO_TABLE).exists()


def test_delay_table_lists_missed_insiders(two_files, tmp_path):
    table = ev.delay_table(two_files)
    assert len(table) == 4
    for _, row in table.iterrows():
        r = ev.evaluate_file([p for p in two_files if p.stem == row["model"]][0])
        point = r["operating_points"][row["operating_point"]]
        assert row["n_missed"] == point["n_missed"] and row["user_recall"] == point["user_recall"]
        per_user = r["delay_per_user"][row["operating_point"]]
        missed = sorted(per_user.loc[per_user["delay_days"].isna(), "user"])
        assert row["missed_insiders"] == ";".join(missed)
        assert row["n_detected"] + row["n_missed"] == row["n_insiders"]
    assert (tmp_path / "tables" / ev.DELAY_TABLE).exists()


def test_confusion_grid_writes_f5(two_files, tmp_path):
    fig = ev.plot_confusion_grid(two_files)
    assert len(fig.axes) == 2
    assert (tmp_path / "figures" / "F5_confusion_best_f1.png").exists()
    assert (tmp_path / "figures" / "F5_confusion_best_f1.pdf").exists()


def test_timing_table_merges_every_source(two_files, tmp_path):
    tables = tmp_path / "tables"
    tables.mkdir()
    pd.DataFrame({"model": ["xgboost"], "fit_seconds_mean": [11.0], "fit_seconds_std": [0.5],
                  "score_seconds_per_1000_mean": [0.001], "score_seconds_per_1000_std": [0.0001],
                  "repeats": [3], "cpu": ["Apple M1"], "threads": [8], "ram_gb": [8.0]}
                 ).to_csv(tables / "timing_supervised.csv", index=False)
    pd.DataFrame({"model": ["iforest"], "test_pr_auc": [0.01], "fit_seconds": [4.0],
                  "score_seconds_per_1000": [0.002], "timing_runs": [3], "cpu": ["Apple M1"],
                  "cores": [8], "threads": [8], "ram_gb": [8.0]}
                 ).to_csv(tables / "unsupervised_extra.csv", index=False)
    pd.DataFrame({"step": ["labels (S6)"], "seconds": [0.07], "runs": [3], "measured": [True],
                  "user_days": [330268], "seconds_per_1000_user_days": [0.0002],
                  "cpu": ["Intel"], "threads": [24], "ram_gb": [31.4]}
                 ).to_csv(tables / "data_processing_time.csv", index=False)
    delay = ev.delay_table(two_files)
    t8 = ev.timing_table(delay=delay)
    assert list(t8["component"]) == ["iforest", "xgboost", "labels (S6)"]
    assert list(t8["kind"]) == ["model", "model", "data processing"]
    rows = t8.set_index("component")
    assert rows.loc["xgboost", "fit_seconds"] == 11.0 and rows.loc["xgboost", "fit_seconds_std"] == 0.5
    assert rows.loc["iforest", "inference_seconds_per_1000"] == 0.002
    assert np.isnan(rows.loc["iforest", "fit_seconds_std"])          # not measured by A17
    assert rows.loc["labels (S6)", "seconds"] == 0.07
    best = delay[delay["operating_point"] == "best_f1"].set_index("model")
    assert rows.loc["xgboost", "median_delay_days_best_f1"] == best.loc["xgboost", "median_delay_days"]
    assert np.isnan(rows.loc["labels (S6)", "median_delay_days_best_f1"])
    assert (tables / ev.T8_TABLE).exists()


def test_timing_table_skips_missing_sources(two_files, tmp_path):
    t8 = ev.timing_table(save=False)
    assert t8.empty


# ---------------------------------------------------------------- Y20: FP/FN analysis
@pytest.fixture
def fpfn_case():
    """8 test user-days (+2 val), threshold 0.5. Outcomes, in order:
    A Mon TP, A Tue FN, B Mon FP (0.9), B Tue FP (0.6), C Mon TN, C Tue TN, D Mon FN, D Tue TP."""
    dates = pd.to_datetime(["2011-02-07", "2011-02-08"] * 4)      # Mon, Tue
    scores = pd.DataFrame({
        "user": ["A", "A", "B", "B", "C", "C", "D", "D"], "date": dates, "split": "test",
        "label": [1, 1, 0, 0, 0, 0, 1, 1], "scenario": [2, 2, 0, 0, 0, 0, 1, 1],
        "score": [0.8, 0.1, 0.9, 0.6, 0.2, 0.3, 0.4, 0.7]})
    val = pd.DataFrame({"user": ["A", "B"], "date": pd.to_datetime(["2011-01-03"] * 2),
                        "split": "val", "label": [1, 0], "scenario": [2, 0], "score": [0.5, 0.1]})
    features = scores[["user", "date"]].assign(
        role=["Eng", "Eng", "Sales", "Sales", "Sales", "Sales", "Eng", "Eng"],
        department=["R&D"] * 2 + ["Field"] * 4 + ["R&D"] * 2,
        label=9, split="x",                                        # must not override the scores
        z_user_http_count=[0, 0, 5.0, -1.0, 0, 0, 0, 0],
        z_user_usb_connect=[0, 0, -7.0, 0.5, 0, 0, 0, 0],
        z_user_email_sent=[0, 0, 1.0, 3.0, 0, 0, 0, 0],
        f_http_count=[0, 0, 99.0, 99.0, 0, 0, 0, 0])
    return pd.concat([scores, val], ignore_index=True), features


def test_fp_fn_rows_marks_every_test_row(fpfn_case):
    scores, features = fpfn_case
    rows = ev.fp_fn_rows(scores, features, threshold=0.5)
    assert len(rows) == 8 and set(rows["split"]) == {"test"}
    assert list(rows["outcome"]) == ["TP", "FN", "FP", "FP", "TN", "TN", "FN", "TP"]
    assert list(rows["weekday"][:2]) == ["Monday", "Tuesday"]
    assert list(rows["label"]) == [1, 1, 0, 0, 0, 0, 1, 1]                # from the score file
    assert rows.loc[2, "role"] == "Sales" and rows.attrs["threshold"] == 0.5
    picked = ev.fp_fn_rows(scores, features)                                # best-F1 from val
    assert picked.attrs["threshold"] == ev.threshold_best_f1(scores[scores["split"] == "val"])
    with pytest.raises(ValueError, match="threshold_type"):
        ev.fp_fn_rows(scores, features, threshold_type="median")


def test_fp_breakdown_counts_and_rates(fpfn_case):
    rows = ev.fp_fn_rows(*fpfn_case, threshold=0.5)
    table = ev.fp_breakdown(rows)
    assert list(table.columns) == ["dimension", "value", "n_normal", "n_fp", "fp_rate", "share_of_fp"]
    role = table[table["dimension"] == "role"].set_index("value")
    assert role.loc["Sales", "n_normal"] == 4 and role.loc["Sales", "n_fp"] == 2
    assert role.loc["Sales", "fp_rate"] == 0.5 and role.loc["Sales", "share_of_fp"] == 1.0
    assert "Eng" not in role.index                     # no normal Eng rows: FPs come from normal days
    user = table[table["dimension"] == "user"]
    assert list(user["value"]) == ["B"]                                     # users with an FP only
    assert list(table["dimension"].unique()) == ["role", "department", "weekday", "user"]


def test_top_deviations_lists_each_fps_largest_z_user_features(fpfn_case):
    rows = ev.fp_fn_rows(*fpfn_case, threshold=0.5)
    top = ev.top_deviations(rows, n=10, k=2)
    assert len(top) == 2 and list(top["score"]) == [0.9, 0.6]               # FPs, highest first
    first = top.iloc[0]
    assert first["dev_1"] == "z_user_usb_connect" and first["dev_1_z"] == -7.0   # by |z|
    assert first["dev_2"] == "z_user_http_count" and first["dev_2_z"] == 5.0
    assert top.iloc[1]["dev_1"] == "z_user_email_sent"
    assert "f_http_count" not in set(top[["dev_1", "dev_2"]].stack())
    assert len(ev.top_deviations(rows, n=1, k=2)) == 1


def test_fn_breakdown_per_insider(fpfn_case):
    rows = ev.fp_fn_rows(*fpfn_case, threshold=0.5)
    table = ev.fn_breakdown(rows)
    assert list(table["user"]) == ["D", "A"]                               # by scenario, then user
    a = table.set_index("user").loc["A"]
    assert (a["scenario"], a["n_malicious_days"], a["n_detected"], a["n_missed"]) == (2, 2, 1, 1)
    assert a["missed_share"] == 0.5 and a["missed_days"] == "2011-02-08"
    assert a["first_malicious_day"] == "2011-02-07" and a["first_detected_day"] == "2011-02-07"
    d = table.set_index("user").loc["D"]
    assert d["first_detected_day"] == "2011-02-08"


def test_fpfn_analysis_picks_the_best_models_and_saves(fpfn_case, tmp_path, monkeypatch):
    scores, features = fpfn_case
    monkeypatch.setattr(ev, "SCORES_DIR", tmp_path)
    monkeypatch.setattr(ev, "TABLES_DIR", tmp_path / "tables")
    for model, bonus in (("xgboost", 0.0), ("random_forest", 0.9), ("iforest", 0.3),
                         ("autoencoder", 0.0), ("ocsvm", 0.9)):
        s = scores.copy()
        s.loc[s["label"] == 0, "score"] -= bonus                           # bigger bonus = better
        s.to_parquet(tmp_path / f"{model}.parquet")
    t5 = ev.compare_files([tmp_path / f"{m}.parquet" for m in ev.MAIN_MODELS])
    picked = ev.pick_fpfn_models(t5)
    assert picked == {"supervised": "random_forest", "unsupervised": "ocsvm"}
    out = ev.fpfn_analysis(features=features, t5=t5)
    for name in (ev.FP_BREAKDOWN_TABLE, ev.FN_TABLE):
        saved = pd.read_csv(tmp_path / "tables" / name)
        assert set(saved["model"]) == {"random_forest", "ocsvm"}, name
    assert (tmp_path / "tables" / ev.FP_TOP_TABLE).exists()    # empty here: both models have no FP
    assert out["fp_top"].empty
    assert set(out) == {"models", "fp_breakdown", "fp_top", "fn"}
