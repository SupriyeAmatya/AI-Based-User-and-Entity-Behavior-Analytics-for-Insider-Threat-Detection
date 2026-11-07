"""S20b "Done when" checks on the committed outputs of `bash scripts/rebuild_data.sh`.

These read files tracked in Git (results/tables/*.csv, notebooks 01-02, Supriye's src files), so
they run on a fresh clone without data/. Run: python -m pytest tests/test_rebuild_outputs.py
"""
import json
from pathlib import Path

import pandas as pd
import pytest

from src.labels import split_is_valid

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
NOTEBOOKS = [ROOT / "notebooks" / "01_eda.ipynb", ROOT / "notebooks" / "02_feature_engineering.ipynb"]
# Supriye's files that carried the S8 decisions (TEAM_PLAN 2.5.8). Other owners' PROVISIONAL tags
# (e.g. Arva's tuned defaults) are their own open decisions and are not checked here.
DECISION_FILES = ["src/config.py", "src/labels.py", "src/features.py", "src/baseline.py",
                  "docs/feature_dictionary.md", *[str(p.relative_to(ROOT)) for p in NOTEBOOKS]]


@pytest.mark.parametrize("name", DECISION_FILES)
def test_no_provisional_values_left(name):
    """S8 is final (Nov 6): no PROVISIONAL tag may remain in the files that hold the decisions."""
    assert "PROVISIONAL" not in (ROOT / name).read_text(encoding="utf-8")


def test_committed_split_covers_every_scenario():
    """The committed split check is valid: every split has malicious days of all 3 scenarios."""
    table = pd.read_csv(TABLES / "split_check.csv", index_col=0)
    assert list(table.index) == ["train", "val", "test"]
    assert split_is_valid(table)


def test_committed_v1_checks_pass():
    """Checks 1, 2, 3 and 5 PASS and the automated recount (check 4) MATCHes; nothing FAILs."""
    checks = pd.read_csv(TABLES / "v1_validation_checks.csv")
    assert len(checks) == 5
    assert not checks["result"].str.contains("FAIL|MISMATCH").any()
    assert (checks["result"].str.contains("PASS|MATCH")).all()


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_ran_top_to_bottom(path):
    """Restart & Run All (TEAM_PLAN 2.5.7): every code cell ran once, in order, with no error."""
    cells = [c for c in json.loads(path.read_text(encoding="utf-8"))["cells"]
             if c["cell_type"] == "code"]
    assert cells, "notebook has no code cells"
    assert [c.get("execution_count") for c in cells] == list(range(1, len(cells) + 1))
    errors = [o for c in cells for o in c.get("outputs", []) if o.get("output_type") == "error"]
    assert not errors, errors[0].get("ename")
