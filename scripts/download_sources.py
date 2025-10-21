#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from typing import List
import requests

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_DIR = DATA_DIR / "raw"
SOURCES_CSV = DATA_DIR / "sources" / "sources.csv"

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"


def safe_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in name)[:160]


def download_file(url: str, dest: Path) -> None:
    headers = {"User-Agent": USER_AGENT}
    with requests.get(url, headers=headers, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def main(args: List[str]) -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if not SOURCES_CSV.exists():
        print(f"Sources file not found: {SOURCES_CSV}", file=sys.stderr)
        return 1

    with open(SOURCES_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            source_id = row.get("source_id", "").strip()
            url = row.get("url", "").strip()
            title = row.get("title", "").strip() or source_id
            if not source_id or not url:
                continue
            ext = "pdf" if ".pdf" in url.lower() else "html"
            fname = f"{safe_filename(source_id + '_' + title)}.{ext}"
            dest = RAW_DIR / fname
            if dest.exists() and dest.stat().st_size > 0:
                print(f"[skip] {dest.name} exists")
                continue
            try:
                print(f"[get] {url} -> {dest.name}")
                download_file(url, dest)
            except Exception as e:
                print(f"[warn] failed {source_id}: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
