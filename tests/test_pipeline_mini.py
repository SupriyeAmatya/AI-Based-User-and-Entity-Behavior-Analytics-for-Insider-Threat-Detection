"""End-to-end test of S4 -> S9 on a miniature CERT r4.2 archive (no real data needed).

The fake archive has the same layout, file names, columns and date format as r4.2:
8 users, one insider per scenario, weekly activity from Jan 2010 to May 2011, and each insider
has malicious days in all three splits so the split check can pass.
"""
import csv
import io
import tarfile

import pandas as pd
import pytest

from src import data_loader, features, labels

FMT = "%m/%d/%Y %H:%M:%S"
INSIDERS = {"AAA0001": 1, "BBB0002": 2, "CCC0003": 3}
NORMAL = ["DDD0004", "EEE0005", "FFF0006", "GGG0007", "HHH0008"]
USERS = list(INSIDERS) + NORMAL
DAYS = pd.date_range("2010-01-04", "2011-05-16", freq="7D")
MALICIOUS_DAYS = [pd.Timestamp("2010-03-15"), pd.Timestamp("2010-12-06"), pd.Timestamp("2011-03-14")]


def _csv(rows, header):
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buf.getvalue().encode()


def _add(tar, name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    tar.addfile(info, io.BytesIO(data))


def _make_archives(raw):
    ids = iter(range(10**6))
    logon, device, file_, email, http = [], [], [], [], []
    answers = {u: [] for u in INSIDERS}

    def rec(table, kind, user, ts, *rest, malicious=False):
        row = [f"{{ID-{next(ids)}}}", ts.strftime(FMT), user, f"PC-{USERS.index(user)}", *rest]
        table.append(row)
        if malicious:
            answers[user].append([kind, *row])

    for day in DAYS:
        for user in USERS:
            rec(logon, "logon", user, day + pd.Timedelta(hours=8), "Logon")
            rec(logon, "logon", user, day + pd.Timedelta(hours=17), "Logoff")
            rec(email, "email", user, day + pd.Timedelta(hours=10), "colleague@dtaa.com", "", "",
                f"{user.lower()}@dtaa.com", "1000", "0", "hello")
            rec(http, "http", user, day + pd.Timedelta(hours=11), "http://www.example.com/page", "words")
    for user, scenario in INSIDERS.items():
        for day in MALICIOUS_DAYS:
            night = day + pd.Timedelta(hours=22, minutes=30)
            rec(logon, "logon", user, night, "Logon", malicious=True)
            rec(device, "device", user, night + pd.Timedelta(minutes=5), "Connect", malicious=True)
            rec(file_, "file", user, night + pd.Timedelta(minutes=6), "secret.doc", "x", malicious=True)
            rec(email, "email", user, night + pd.Timedelta(minutes=7), "rival@competitor.com", "", "",
                f"{user.lower()}@dtaa.com", "50000", "2", "files", malicious=True)
            rec(http, "http", user, night + pd.Timedelta(minutes=8), "http://wikileaks.org/x", "w",
                malicious=True)
    logon.append(list(logon[0]))  # one exact duplicate record (same id) for the cleaning report

    base = ["id", "date", "user", "pc"]
    months = pd.period_range("2009-12", "2011-05", freq="M")
    ldap_header = ["employee_name", "user_id", "email", "role", "business_unit", "functional_unit",
                   "department", "team", "supervisor"]
    ldap_rows = [[u, u, f"{u.lower()}@dtaa.com", "ITAdmin" if u in ("CCC0003", "HHH0008") else "Salesman",
                  "1", "fu", "dept", "team", "boss"] for u in USERS]
    with tarfile.open(raw / "r4.2.tar.bz2", "w:bz2") as tar:
        _add(tar, "r4.2/file.csv", _csv(file_, base + ["filename", "content"]))
        for month in months:
            _add(tar, f"r4.2/LDAP/{month}.csv", _csv(ldap_rows, ldap_header))
        _add(tar, "r4.2/psychometric.csv", _csv([[u, u, 30, 30, 30, 30, 30] for u in USERS],
                                                 ["employee_name", "user_id", "O", "C", "E", "A", "N"]))
        _add(tar, "r4.2/logon.csv", _csv(logon, base + ["activity"]))
        _add(tar, "r4.2/device.csv", _csv(device, base + ["activity"]))
        _add(tar, "r4.2/email.csv", _csv(email, base + ["to", "cc", "bcc", "from", "size",
                                                        "attachments", "content"]))
        _add(tar, "r4.2/http.csv", _csv(http, base + ["url", "content"]))

    insiders = [["4.1", 1, "r4.1-1.csv", "ZZZ9999", "01/01/2010 00:00:00", "01/02/2010 00:00:00"]]
    for user, scenario in INSIDERS.items():
        insiders.append(["4.2", scenario, f"r4.2-{scenario}-{user}.csv", user,
                         MALICIOUS_DAYS[0].strftime(FMT), (MALICIOUS_DAYS[-1] + pd.Timedelta(days=1)).strftime(FMT)])
    with tarfile.open(raw / "answers.tar.bz2", "w:bz2") as tar:
        _add(tar, "answers/insiders.csv",
             _csv(insiders, ["dataset", "scenario", "details", "user", "start", "end"]))
        for user, scenario in INSIDERS.items():
            body = "".join(",".join(r) + "\n" for r in answers[user]).encode()
            _add(tar, f"answers/r4.2-{scenario}/r4.2-{scenario}-{user}.csv", body)


@pytest.fixture
def mini(tmp_path, monkeypatch):
    raw, parquet, processed, tables = (tmp_path / d for d in ("raw", "parquet", "processed", "tables"))
    raw.mkdir()
    _make_archives(raw)
    for name, value in {"RAW_DIR": raw, "CERT_ARCHIVE": raw / "r4.2.tar.bz2",
                        "ANSWERS_ARCHIVE": raw / "answers.tar.bz2", "CERT_SMALL_DIR": raw / "r4.2",
                        "ANSWERS_DIR": raw / "answers", "PARQUET_DIR": parquet}.items():
        monkeypatch.setattr(data_loader, name, value)
    monkeypatch.setattr(labels, "ANSWERS_DIR", raw / "answers")
    monkeypatch.setattr(labels, "PROCESSED_DIR", processed)
    monkeypatch.setattr(labels, "TABLES_DIR", tables)
    monkeypatch.setattr(features, "PROCESSED_DIR", processed)
    monkeypatch.setattr(features, "V0_N_INSIDERS", 3)
    monkeypatch.setattr(features, "V0_N_NORMAL", 4)
    return tmp_path


def test_s4_conversion_and_s5_loaders(mini):
    manifest = data_loader.convert_cert_to_parquet()
    assert set(manifest) == {"logon", "device", "file", "email", "http"}
    n_days, n_users = len(DAYS), len(USERS)
    assert manifest["logon"]["rows"] == 2 * n_days * n_users + 3 * 3 + 1
    assert "content" not in manifest["http"]["columns"] and "content" not in manifest["email"]["columns"]
    assert (mini / "raw" / "r4.2" / "LDAP" / "2010-01.csv").exists()
    assert (mini / "raw" / "answers" / "insiders.csv").exists()

    logon = data_loader.load_logon()
    assert data_loader.CLEANING_REPORT["logon"]["duplicates_removed"] == 1
    assert {"day", "hour"} <= set(logon.columns)
    # a column subset must not merge different events: every row has the same few users
    subset = data_loader.load_logon(columns=["user"])
    assert len(subset) == len(logon) and list(subset.columns) == ["user"]
    assert len(data_loader.load_email(users=["AAA0001"])) == n_days + 3
    ldap = data_loader.load_ldap()
    assert ldap["month"].nunique() == 18 and {"role", "department", "email"} <= set(ldap.columns)
    insiders = data_loader.load_insiders()
    assert sorted(insiders["user"]) == sorted(INSIDERS)  # the 4.1 row is filtered out


def test_s6_labels_and_s8_split(mini, capsys):
    data_loader.convert_cert_to_parquet()
    lab, records, checks = labels.build_labels()
    assert checks["records_user_not_insider"] == 0 and checks["records_outside_start_end"] == 0
    assert checks["insiders_per_scenario_answers"] == {1: 1, 2: 1, 3: 1}
    assert len(lab) == 3 * 3 and set(lab["day"]) == set(MALICIOUS_DAYS)
    labels.main()
    out = capsys.readouterr().out
    assert "OK, every split has every scenario" in out
    assert (mini / "processed" / "labels.parquet").exists()
    assert (mini / "tables" / "insider_timeline.csv").exists()


def test_s9_feature_table_v0(mini):
    data_loader.convert_cert_to_parquet()
    labels.main()
    features.main(["v0"])
    df = pd.read_parquet(mini / "processed" / "features_v0.parquet")
    assert list(df.columns[:8]) == features.META_COLUMNS
    assert df["user"].nunique() == 7                       # 3 insiders + 4 of the 5 normal users
    assert not df.duplicated(["user", "date"]).any()
    mal = df[df["label"] == 1]
    assert len(mal) == 9 and set(mal["scenario"]) == {1, 2, 3}
    assert set(mal["split"]) == {"train", "val", "test"}
    assert (mal["f_afterhours_logon"] == 1).all() and (mal["f_usb_connect"] == 1).all()
    assert (mal["f_email_external"] == 1).all() and (mal["f_file_copy"] == 1).all()
    normal = df[df["label"] == 0]
    assert (normal["f_afterhours_logon"] == 0).all() and (normal["f_email_external"] == 0).all()
    assert set(df.loc[df["user"] == "CCC0003", "role"]) == {"ITAdmin"}
    assert df.loc[df["user"] == "AAA0001", "insider"].eq(1).all()
    X, y, cols = features.get_model_matrix(df, split="train")
    assert len(X) == (df["split"] == "train").sum() and int(y.sum()) == 3
