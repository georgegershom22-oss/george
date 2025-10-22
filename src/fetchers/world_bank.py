import os
from typing import Dict, List
import csv
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

WB_BASE = "https://api.worldbank.org/v2/country/NGA/indicator/{indicator}?format=json&per_page=20000"

INDICATORS = {
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",  # GDP growth (annual %)
    "inflation": "FP.CPI.TOTL.ZG",      # Inflation, consumer prices (annual %)
    "lending_rate": "FR.INR.LEND",      # Lending interest rate (%)
    "ease_of_doing_business": "IC.BUS.EASE.XQ",  # Ease of Doing Business rank (1=best)
    # Ease of Doing Business historical (2019 last). Use LPI as proxy if not available.
}


def fetch_indicator(indicator_code: str) -> List[Dict]:
    url = WB_BASE.format(indicator=indicator_code)
    try:
        with urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (URLError, HTTPError) as e:
        raise RuntimeError(f"WB fetch failed: {e}")
    if not isinstance(data, list) or len(data) < 2:
        raise RuntimeError(f"Unexpected WB response for {indicator_code}")
    rows = data[1] if len(data) > 1 and isinstance(data[1], list) else []
    out: List[Dict] = []
    for row in rows:
        date = row.get("date")
        val = row.get("value")
        try:
            year = int(date)
        except Exception:
            continue
        if val is None:
            continue
        try:
            value = float(val)
        except Exception:
            continue
        out.append({"year": year, "value": value})
    out.sort(key=lambda r: r["year"])
    return out


def fetch_all(save_dir: str) -> Dict[str, str]:
    os.makedirs(save_dir, exist_ok=True)
    paths: Dict[str, str] = {}
    for name, code in INDICATORS.items():
        try:
            records = fetch_indicator(code)
            out = os.path.join(save_dir, f"wb_{name}.csv")
            with open(out, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["year", "value"])
                writer.writeheader()
                for r in records:
                    writer.writerow(r)
            paths[name] = out
        except Exception as e:
            out = os.path.join(save_dir, f"wb_{name}_ERROR.txt")
            with open(out, "w", encoding="utf-8") as f:
                f.write(str(e))
            paths[name] = out
    return paths
