"""Loading the CERT r4.2 logs (owner: Supriye; tasks S4 and S5).

S4 - convert once, from the repo root:
    python -m src.data_loader convert

    Streams data/raw/r4.2.tar.bz2 in a single pass. The five big logs (logon, device, file,
    email, http) are written to data/parquet/<log>.parquet in 1M-row chunks, so the ~16 GB of
    CSVs are never unpacked to disk. The `content` column is dropped from http and email to save
    space (it is still in the archive if ever needed). Small files (LDAP/, psychometric.csv) are
    extracted to data/raw/r4.2/, and answers.tar.bz2 to data/raw/answers/.
    Row counts and date ranges are saved to data/parquet/manifest.json.

S5 - load clean tables:
    from src.data_loader import load_logon
    logon = load_logon()                       # every user
    logon = load_logon(users=["AAM0658"])      # only some users (fast: Parquet filter)
    Each loader parses `date`, adds `day` (midnight) and `hour` (decimal), strips whitespace from
    user/pc, drops exact duplicate rows and rows with no date or user. What was removed is kept
    in CLEANING_REPORT (see cleaning_report()).
"""
import json
import sys
import tarfile
import time

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.config import (
    ANSWERS_ARCHIVE, ANSWERS_DIR, CERT_ARCHIVE, CERT_SMALL_DIR, LOGS, PARQUET_DIR, RAW_DIR,
)

DATE_FORMAT = "%m/%d/%Y %H:%M:%S"
DROP_COLUMNS = {"http": ["content"], "email": ["content"]}
INT_COLUMNS = {"size", "attachments"}
CHUNK_ROWS = 1_000_000
CLEANING_REPORT = {}


# ---------------------------------------------------------------- S4: conversion
def _arrow_schema(columns):
    fields = []
    for c in columns:
        if c == "date":
            fields.append(pa.field(c, pa.timestamp("ns")))
        elif c in INT_COLUMNS:
            fields.append(pa.field(c, pa.int64()))
        else:
            fields.append(pa.field(c, pa.string()))
    return pa.schema(fields)


def _convert_csv(fileobj, log):
    """Stream one CSV into data/parquet/<log>.parquet; return its manifest entry."""
    drop = DROP_COLUMNS.get(log, [])
    reader = pd.read_csv(fileobj, chunksize=CHUNK_ROWS, dtype=str, keep_default_na=False,
                         na_values=[""], usecols=lambda c: c not in drop)
    out = PARQUET_DIR / f"{log}.parquet"
    writer, schema = None, None
    rows, date_min, date_max = 0, None, None
    started = time.perf_counter()
    for chunk in reader:
        chunk["date"] = pd.to_datetime(chunk["date"], format=DATE_FORMAT)
        for c in INT_COLUMNS & set(chunk.columns):
            chunk[c] = pd.to_numeric(chunk[c]).astype("Int64")  # nullable: a blank value stays missing
        if writer is None:
            schema = _arrow_schema(chunk.columns)
            writer = pq.ParquetWriter(out, schema, compression="snappy")
        writer.write_table(pa.Table.from_pandas(chunk, schema=schema, preserve_index=False))
        rows += len(chunk)
        lo, hi = chunk["date"].min(), chunk["date"].max()
        date_min = lo if date_min is None else min(date_min, lo)
        date_max = hi if date_max is None else max(date_max, hi)
        print(f"  {log}: {rows:,} rows", end="\r", flush=True)
    writer.close()
    print(f"  {log}: {rows:,} rows in {time.perf_counter() - started:.0f}s")
    return {"rows": rows, "date_min": str(date_min), "date_max": str(date_max),
            "columns": list(schema.names), "dropped_columns": drop}


def _safe_relative(name, prefix):
    """Path of an archive member relative to `prefix`, refusing anything that escapes it."""
    rel = name[len(prefix):].lstrip("/")
    if not name.startswith(prefix) or ".." in rel.split("/") or rel.startswith("/"):
        raise ValueError(f"unexpected archive member {name!r}")
    return rel


def convert_cert_to_parquet():
    """S4: one streaming pass over r4.2.tar.bz2, plus extraction of answers.tar.bz2."""
    PARQUET_DIR.mkdir(parents=True, exist_ok=True)
    CERT_SMALL_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {}
    with tarfile.open(CERT_ARCHIVE, "r|bz2") as tar:
        for member in tar:
            if not member.isfile():
                continue
            rel = _safe_relative(member.name, "r4.2")
            log = rel[:-4] if rel.endswith(".csv") else None
            if log in LOGS:
                print(f"converting {rel} ({member.size / 1e9:.2f} GB)")
                manifest[log] = _convert_csv(tar.extractfile(member), log)
            else:
                target = CERT_SMALL_DIR / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(tar.extractfile(member).read())
    with tarfile.open(ANSWERS_ARCHIVE, "r:bz2") as tar:
        tar.extractall(RAW_DIR, filter="data")
    (PARQUET_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
    missing = set(LOGS) - set(manifest)
    if missing:
        raise RuntimeError(f"logs not found in the archive: {sorted(missing)}")
    return manifest


def read_manifest():
    return json.loads((PARQUET_DIR / "manifest.json").read_text())


# ---------------------------------------------------------------- S5: loaders
def _clean(df, log, keep_columns=None):
    """Clean one log. Duplicates are judged on the full record including its unique `id`, so two
    different events that look alike in a column subset are never merged; `id` is then dropped
    again unless the caller asked for it (`keep_columns`)."""
    rows_in = len(df)
    if "date" in df and not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"], format=DATE_FORMAT)
    for c in ("user", "pc"):
        if c in df:
            df[c] = df[c].str.strip()
    key = [c for c in ("date", "user") if c in df]
    no_key = int(df[key].isna().any(axis=1).sum()) if key else 0
    df = df.dropna(subset=key)
    before_dedup = len(df)
    df = df.drop_duplicates()
    if keep_columns is not None and "id" not in keep_columns:
        df = df.drop(columns="id")
    if "date" in df:
        df["day"] = df["date"].dt.normalize()
        df["hour"] = df["date"].dt.hour + df["date"].dt.minute / 60
    CLEANING_REPORT[log] = {"rows_in": rows_in, "missing_key_removed": no_key,
                            "duplicates_removed": before_dedup - len(df), "rows_out": len(df)}
    return df.reset_index(drop=True)


def _load_log(log, columns=None, users=None):
    filters = [("user", "in", list(users))] if users is not None else None
    read = None if columns is None else list(dict.fromkeys(["id", *columns]))
    df = pd.read_parquet(PARQUET_DIR / f"{log}.parquet", columns=read, filters=filters)
    return _clean(df, log, keep_columns=columns)


def load_logon(columns=None, users=None):
    return _load_log("logon", columns, users)


def load_device(columns=None, users=None):
    return _load_log("device", columns, users)


def load_file(columns=None, users=None):
    return _load_log("file", columns, users)


def load_email(columns=None, users=None):
    return _load_log("email", columns, users)


def load_http(columns=None, users=None):
    """http is ~28M rows: pass `columns` and/or `users`, or use iter_http_batches()."""
    return _load_log("http", columns, users)


def iter_http_batches(columns=("user", "date", "url"), batch_rows=CHUNK_ROWS):
    """Yield the http log as DataFrames of `batch_rows` rows, for aggregations that must not
    load all of it at once (S7 domain counts, S15 web features). Rows are not cleaned."""
    parquet = pq.ParquetFile(PARQUET_DIR / "http.parquet")
    for batch in parquet.iter_batches(batch_size=batch_rows, columns=list(columns)):
        yield batch.to_pandas()


def load_ldap():
    """All monthly LDAP snapshots stacked, with a `month` column (first day of that month)."""
    frames = []
    for path in sorted((CERT_SMALL_DIR / "LDAP").glob("*.csv")):
        df = pd.read_csv(path, dtype=str)
        df.columns = [c.strip().lower() for c in df.columns]
        df["month"] = pd.Timestamp(path.stem + "-01")
        frames.append(df)
    if not frames:
        raise FileNotFoundError(f"no LDAP files in {CERT_SMALL_DIR / 'LDAP'}; run the conversion first")
    ldap = pd.concat(frames, ignore_index=True)
    ldap["user_id"] = ldap["user_id"].str.strip()
    return ldap


def load_psychometric():
    df = pd.read_csv(CERT_SMALL_DIR / "psychometric.csv", dtype={"user_id": str})
    df.columns = [c.strip() for c in df.columns]
    df["user_id"] = df["user_id"].str.strip()
    return df


def load_insiders():
    """answers/insiders.csv rows for dataset r4.2, with parsed start/end times."""
    df = pd.read_csv(ANSWERS_DIR / "insiders.csv", dtype=str)
    df = df[df["dataset"].str.strip() == "4.2"].copy()
    df["scenario"] = df["scenario"].astype(int)
    for c in ("start", "end"):
        df[c] = pd.to_datetime(df[c], format=DATE_FORMAT)
    return df.reset_index(drop=True)


def recipient_domains(email: pd.DataFrame) -> pd.Series:
    """Lower-cased recipient domains (to + cc + bcc) of each email, as a list per row."""
    recipients = email[["to", "cc", "bcc"]].fillna("").agg(";".join, axis=1)
    return recipients.str.lower().str.findall(r"@([\w.-]+)")


def cleaning_report():
    """Rows removed by the loaders called so far in this session (for the paper, S5 step 4)."""
    return pd.DataFrame(CLEANING_REPORT).T


if __name__ == "__main__":
    if sys.argv[1:] == ["convert"]:
        for log, info in convert_cert_to_parquet().items():
            print(f"{log:7s} {info['rows']:>12,} rows  {info['date_min']} -> {info['date_max']}")
    else:
        print(__doc__)
