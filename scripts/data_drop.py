"""The one data drop (owner: Supriye; S4/S20, TEAM_PLAN 2.5.12).

Everything Arva and Ayo need, in one zip, sent once:

    python scripts/data_drop.py make      # Supriye: -> data/ueba_data_v1.zip (~380 MB)
    python scripts/data_drop.py verify    # Arva, Ayo: after unzipping in the repo root

The zip holds data/processed/ (labels, feature tables v0/v1, the web-log cache, domain counts),
the 4 small logs in data/parquet/ (+ manifest.json), data/CHECKSUMS.txt (SHA-256 of every file) and
data/DROP_INFO.txt (the commit and the config decisions it was built with). http.parquet (907 MB)
and the raw archives are left out on purpose: nobody but Supriye needs them.
"""
import hashlib
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "ueba_data_v1"
FILES = [
    "data/processed/labels.parquet",
    "data/processed/features_v0.parquet",
    "data/processed/features_v1.parquet",
    "data/processed/http_user_day_domain.parquet",
    "data/processed/http_domain_counts.csv",
    "data/parquet/logon.parquet",
    "data/parquet/device.parquet",
    "data/parquet/file.parquet",
    "data/parquet/email.parquet",
    "data/parquet/manifest.json",
]
CHECKSUMS = "data/CHECKSUMS.txt"
INFO = "data/DROP_INFO.txt"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _git_commit(root: Path) -> str:
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True,
                                text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=root,
                               capture_output=True, text=True, check=True).stdout.strip()
        return commit + (" (uncommitted changes)" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _decisions() -> list:
    """The src/config.py values the data was built with, so teammates can see them."""
    try:
        sys.path.insert(0, str(ROOT))
        from src import config
    except ImportError:
        return ["(src/config.py not importable)"]
    return [f"TRAIN_END = {config.TRAIN_END}", f"VAL_END = {config.VAL_END}",
            f"WORK_START_HOUR = {config.WORK_START_HOUR}", f"WORK_END_HOUR = {config.WORK_END_HOUR}",
            f"EMAIL_COUNT_PERSONAL = {config.EMAIL_COUNT_PERSONAL}",
            "HTTP_CATEGORIES = " + ", ".join(f"{k}: {len(v)} domains"
                                             for k, v in config.HTTP_CATEGORIES.items())]


def make(root: Path = ROOT, name: str = NAME, files=FILES) -> Path:
    """Write the checksums and info file, then the zip. Stops if any file is missing."""
    missing = [f for f in files if not (root / f).is_file()]
    if missing:
        raise FileNotFoundError("missing, rebuild first (scripts/rebuild_data.sh): " + ", ".join(missing))
    (root / CHECKSUMS).write_text("".join(f"{sha256(root / f)}  {f}\n" for f in files), encoding="utf-8")
    info = [f"{name}.zip", f"created: {datetime.now().isoformat(timespec='seconds')}",
            f"commit: {_git_commit(root)}", "", "decisions (src/config.py):", *_decisions(), "",
            "files:", *(f"  {f}  ({(root / f).stat().st_size / 2**20:.1f} MB)" for f in files),
            "", "After unzipping in the repo root: python scripts/data_drop.py verify"]
    (root / INFO).write_text("\n".join(info) + "\n", encoding="utf-8")
    out = root / "data" / f"{name}.zip"
    with zipfile.ZipFile(out, "w") as z:
        for f in files:   # Parquet is already compressed, so it is stored as is
            z.write(root / f, f, zipfile.ZIP_STORED if f.endswith(".parquet") else zipfile.ZIP_DEFLATED)
        for f in (CHECKSUMS, INFO):
            z.write(root / f, f, zipfile.ZIP_DEFLATED)
    return out


def verify(root: Path = ROOT) -> list:
    """Compare every file listed in data/CHECKSUMS.txt; returns the problems (empty = all good)."""
    listing = root / CHECKSUMS
    if not listing.is_file():
        return [f"{CHECKSUMS} not found: unzip {NAME}.zip in the repo root first"]
    problems = []
    for line in listing.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, f = line.split(maxsplit=1)
        path = root / f
        if not path.is_file():
            problems.append(f"MISSING  {f}")
        elif sha256(path) != expected:
            problems.append(f"CHANGED  {f}")
    return problems


def main(argv):
    if argv[:1] == ["make"]:
        out = make()
        print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size / 2**20:.0f} MB)")
        print((ROOT / INFO).read_text(encoding="utf-8"))
    elif argv[:1] == ["verify"]:
        problems = verify()
        print("\n".join(problems) if problems else f"OK: every file in {CHECKSUMS} matches")
        return 1 if problems else 0
    else:
        print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
