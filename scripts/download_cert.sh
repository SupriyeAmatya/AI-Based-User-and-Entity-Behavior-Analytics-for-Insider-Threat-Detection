#!/usr/bin/env bash
# S1 (owner: Supriye): download CERT r4.2 + answers from CMU KiltHub into data/raw/.
#
#   bash scripts/download_cert.sh            # run from the repo root
#
# KiltHub caps each connection at ~0.4 MB/s, so r4.2.tar.bz2 (4.82 GB) is fetched as N byte ranges
# in parallel. To pause, stop the script (Ctrl+C); run the same command again to resume. Every part
# continues where it stopped. At the end both archives are checked against CHECKSUMS-sha256.txt.
set -euo pipefail
DIR=data/raw
N=16
BASE=https://ndownloader.figshare.com/files
ARCHIVE="$DIR/r4.2.tar.bz2"; ARCHIVE_ID=24856766; TOTAL=4824287500
PARTS="$DIR/.parts"
size() { wc -c < "$1" | tr -d ' '; }
# sha256sum on Linux/Git Bash; macOS ships shasum instead
if command -v sha256sum >/dev/null; then sha256() { sha256sum "$1"; }; else sha256() { shasum -a 256 "$1"; }; fi

mkdir -p "$DIR"
for small in CHECKSUMS-sha256.txt:24857831 SEI_Insider_README.txt:24860765 answers.tar.bz2:24857828; do
  name=${small%%:*}; id=${small##*:}
  [ -s "$DIR/$name" ] || curl -sSL --fail --retry 5 -o "$DIR/$name" "$BASE/$id"
done

if [ -f "$ARCHIVE" ] && [ ! -d "$PARTS" ] && [ "$(size "$ARCHIVE")" -eq "$TOTAL" ]; then
  echo "r4.2.tar.bz2 already complete"
else
  [ -f "$ARCHIVE" ] || : > "$ARCHIVE"
  mkdir -p "$PARTS"
  # Part boundaries are fixed the first time (archive prefix + part count) so a resume reuses them.
  [ -f "$PARTS/start" ] || size "$ARCHIVE" > "$PARTS/start"
  [ -f "$PARTS/n" ] || echo "$N" > "$PARTS/n"
  S=$(cat "$PARTS/start"); N=$(cat "$PARTS/n")
  CH=$(( (TOTAL - S + N - 1) / N ))
  echo "r4.2.tar.bz2: prefix $S of $TOTAL bytes; the rest in $N parallel parts"
  for i in $(seq 0 $((N - 1))); do
    a=$((S + i * CH)); b=$((a + CH - 1)); [ "$b" -ge "$TOTAL" ] && b=$((TOTAL - 1))
    [ "$a" -gt "$b" ] && continue
    p="$PARTS/p$(printf %02d "$i")"; want=$((b - a + 1))
    ( touch "$p"
      while [ "$(size "$p")" -lt "$want" ]; do
        have=$(size "$p")
        curl -sSL --fail -r "$((a + have))-$b" "$BASE/$ARCHIVE_ID" >> "$p" \
          || { echo "part $i interrupted at $have bytes, resuming"; sleep 5; }
      done
      [ "$(size "$p")" -eq "$want" ] || { echo "part $i has the wrong size"; exit 1; }
      echo "part $i done" ) &
  done
  wait
  [ "$(size "$ARCHIVE")" -eq "$S" ] || { echo "archive prefix changed size; not appending" >&2; exit 1; }
  cat "$PARTS"/p* >> "$ARCHIVE"
  rm -r "$PARTS"
fi

echo "verifying checksums..."
for name in r4.2.tar.bz2 answers.tar.bz2; do
  expected=$(grep -E "[[:space:]]\*?$name\$" "$DIR/CHECKSUMS-sha256.txt" | awk '{print $1}')
  actual=$(sha256 "$DIR/$name" | awk '{print $1}')
  if [ "$expected" = "$actual" ]; then echo "  $name OK"; else echo "  $name CHECKSUM MISMATCH" >&2; exit 1; fi
done
