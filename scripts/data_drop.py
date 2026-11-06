"""The one data drop (owner: Supriye; S4/S20, TEAM_PLAN 2.5.12).

Everything Arva and Ayo need, in one zip, sent once:

    python scripts/data_drop.py make      # Supriye: -> data/ueba_data_v1.zip (~360 MB)
    python scripts/data_drop.py verify    # Arva, Ayo: after unzipping in the repo root

The zip holds data/processed/ (labels, feature tables v0/v1, the web-log cache, domain counts),
the 4 small logs in data/parquet/ (+ manifest.json), data/CHECKSUMS.txt (SHA-256 of every file) and
data/DROP_INFO.txt (the commit and the config decisions it was built with). http.parquet (907 MB)
and the raw archives are left out on purpose: nobody but Supriye needs them.

`make` refuses to build when the web-log cache was not built with the current working hours,
because teammates cannot rebuild it without http.parquet: run `python -m src.features v1` first.
"""
import hashlib
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import config  # noqa: E402  (needs ROOT on the path)

NAME = "ueba_data_v1"


def _rel(path: Path) -> str:
    """Archive name of a data path: relative to the repo root, forward slashes."""
    return path.relative_to(config.ROOT).as_posix()


WEB_CACHE = _rel(config.PROCESSED_DIR / "http_user_day_domain.parquet")
FILES = [_rel(config.PROCESSED_DIR / name) for name in (
    "labels.parquet", "features_v0.parquet", "features_v1.parquet",
    "http_user_day_domain.parquet", "http_domain_counts.csv")] + [
    _rel(config.PARQUET_DIR / name) for name in (
        "logon.parquet", "device.parquet", "file.parquet", "email.parquet", "manifest.json")]
CHECKSUMS = _rel(config.ROOT / "data" / "CHECKSUMS.txt")
INFO = _rel(config.ROOT / "data" / "DROP_INFO.txt")
DECISIONS = ("TRAIN_END", "VAL_END", "WORK_START_HOUR", "WORK_END_HOUR", "EMAIL_COUNT_PERSONAL")


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


def decisions() -> list:
    """The src/config.py values the data is built with, one 'NAME = value' line each."""
    lines = [f"{name} = {getattr(config, name, '(not set)')}" for name in DECISIONS]
    categories = getattr(config, "HTTP_CATEGORIES", {})
    lines.append("HTTP_CATEGORIES = " + "; ".join(f"{k}: {', '.join(sorted(v))}"
                                                  for k, v in sorted(categories.items())))
    return lines


def check_web_cache(root: Path) -> None:
    """Refuse a web-log cache built with other working hours (or before the stamp existed)."""
    from src.features import cache_work_hours, work_hours_stamp
    built_with, wanted = cache_work_hours(root / WEB_CACHE), work_hours_stamp()
    if built_with != wanted:
        raise ValueError(f"{WEB_CACHE} was built with working hours {built_with or '(no stamp)'}, "
                         f"but src/config.py says {wanted}. Teammates cannot rebuild it without "
                         f"http.parquet: run `python -m src.features v1` first, then make the drop.")


def make(root: Path = None, name: str = NAME, files=FILES, check_cache=True) -> Path:
    """Write the checksums and info file, then the zip. Stops if a file is missing or the web-log
    cache does not match the current working hours."""
    root = ROOT if root is None else Path(root)
    missing = [f for f in files if not (root / f).is_file()]
    if missing:
        raise FileNotFoundError("missing, rebuild first (scripts/rebuild_data.sh): " + ", ".join(missing))
    if check_cache and WEB_CACHE in files:
        check_web_cache(root)
    (root / CHECKSUMS).write_text("".join(f"{sha256(root / f)}  {f}\n" for f in files), encoding="utf-8")
    info = [f"{name}.zip", f"created: {datetime.now().isoformat(timespec='seconds')}",
            f"commit: {_git_commit(root)}", "", "decisions (src/config.py):", *decisions(), "",
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


def verify(root: Path = None) -> list:
    """Compare every file listed in data/CHECKSUMS.txt; returns the problems (empty = all good)."""
    root = ROOT if root is None else Path(root)
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


def decision_warnings(root: Path = None) -> list:
    """Decisions recorded in DROP_INFO.txt that differ from this checkout's src/config.py (e.g. a
    teammate on an older main). Warnings only: the files themselves can still be fine."""
    root = ROOT if root is None else Path(root)
    info = root / INFO
    if not info.is_file():
        return []
    recorded = {line.split(" = ", 1)[0]: line for line in info.read_text(encoding="utf-8").splitlines()
                if " = " in line}
    return [f"drop: {recorded[line.split(' = ', 1)[0]]}  |  yours: {line}"
            for line in decisions() if line.split(" = ", 1)[0] in recorded
            and recorded[line.split(" = ", 1)[0]] != line]


def main(argv) -> int:
    if argv[:1] == ["make"]:
        try:
            out = make()
        except (FileNotFoundError, ValueError) as error:
            print(f"Not built: {error}")
            return 1
        print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size / 2**20:.0f} MB)")
        print((ROOT / INFO).read_text(encoding="utf-8"))
        return 0
    if argv[:1] == ["verify"]:
        problems = verify()
        print("\n".join(problems) if problems else f"OK: every file in {CHECKSUMS} matches")
        warnings = decision_warnings()
        if warnings:
            print("\nWARNING: the drop was built with other decisions than your src/config.py "
                  "(pull main, or ask Supriye):\n" + "\n".join(warnings))
        return 1 if problems else 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
