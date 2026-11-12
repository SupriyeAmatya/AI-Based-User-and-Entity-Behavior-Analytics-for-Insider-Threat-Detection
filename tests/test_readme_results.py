"""Tests for the README results table (S33 step 2). Run: python -m pytest tests"""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location(
    "readme_results", Path(__file__).resolve().parents[1] / "scripts" / "readme_results.py")
readme_results = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readme_results)


def _t5(**overrides):
    row = {"model": "xgboost", "operating_point": "best_f1", "precision": 0.96449, "recall": 0.95882,
           "f1": 0.96165, "fpr": 0.0000925, "fnr": 0.04118, "roc_auc": 0.99968, "pr_auc": 0.98767,
           "user_recall": 1.0, "median_delay_days": 0.0, "tp": 163}
    row.update(overrides)
    return pd.DataFrame([row])


def test_results_markdown_formats_one_row_per_model_and_point():
    table = pd.concat([_t5(), _t5(model="iforest_contam", operating_point="top_1pct",
                                  median_delay_days=np.nan)], ignore_index=True)
    lines = readme_results.results_markdown(table).splitlines()
    assert len(lines) == 4                                   # header, separator, 2 rows
    assert lines[0].startswith("| Model | Operating point | Precision |")
    assert lines[2] == ("| XGBoost | best-F1 | 0.964 | 0.959 | 0.962 | 0.0001 | 0.041 | 1.000 "
                        "| 0.988 | 1.000 | 0.0 |")
    assert lines[3].startswith("| Isolation Forest, all train rows | top 1% |")
    assert lines[3].endswith("| – |")                        # a missing delay shows as a dash


def test_results_markdown_needs_the_t5_columns():
    with pytest.raises(ValueError, match="pr_auc"):
        readme_results.results_markdown(_t5().drop(columns="pr_auc"))


def test_render_replaces_only_the_marked_block_and_is_idempotent():
    start, end = readme_results.START, readme_results.END
    readme = f"# Title\n\n## Results\n\nIntro.\n\n{start}\nold table\n{end}\n\nAfter.\n"
    once = readme_results.render(readme, _t5())
    assert "old table" not in once and "| XGBoost | best-F1 |" in once
    assert once.startswith("# Title\n\n## Results\n\nIntro.\n\n") and once.endswith(f"{end}\n\nAfter.\n")
    assert readme_results.render(once, _t5()) == once
    with pytest.raises(ValueError, match="marker"):
        readme_results.render("# no markers\n", _t5())
    with pytest.raises(ValueError, match="marker"):
        readme_results.render(f"{end}\n{start}\n", _t5())


def test_read_readme_ignores_windows_line_endings(tmp_path):
    path = tmp_path / "README.md"
    path.write_bytes(b"# Title\r\n\r\nText.\r\n")
    assert readme_results.read_readme(path) == "# Title\n\nText.\n"


def test_readme_matches_the_committed_t5():
    """README.md's table is exactly what model_comparison.csv gives (run the script after a
    `python -m src.evaluate report` that changes T5)."""
    readme = readme_results.read_readme()
    table = pd.read_csv(readme_results.T5)
    assert readme_results.render(readme, table) == readme
    assert set(table["model"]) <= set(readme_results.MODEL_NAMES)
    assert len(table) == 14                                  # 7 score files x 2 operating points
