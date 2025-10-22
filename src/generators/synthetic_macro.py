import os
from typing import Optional, List, Dict
import csv
import random

random.seed(42)


def _ar1_series(start_year: int, end_year: int, mu: float, phi: float, sigma: float, x0: float) -> List[Dict]:
    years = list(range(start_year, end_year + 1))
    x_prev = x0
    out: List[Dict] = []
    for year in years:
        if year == years[0]:
            x = x_prev
        else:
            # white noise ~ N(0, sigma) approximated by Box-Muller
            u1, u2 = random.random(), random.random()
            z = (sigma) * ( (-2.0 * (0.0 if u1 == 0 else (u1))).__neg__() )  # placeholder, will replace below
            # simpler: use random.gauss
            eps = random.gauss(0.0, sigma)
            x = mu + phi * (x_prev - mu) + eps
            x_prev = x
        out.append({"year": year, "value": round(float(x), 4)})
    return out


def _read_csv_records(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        recs: List[Dict] = []
        for row in reader:
            try:
                year = int(float(row.get("year", "")))
                value = float(row.get("value", ""))
            except Exception:
                continue
            recs.append({"year": year, "value": value})
    recs.sort(key=lambda r: r["year"])
    return recs


def generate_macro_series(raw_csv_path: Optional[str], start_year: int, end_year: int,
                          mean: float, phi: float, sigma: float, x0: float) -> List[Dict]:
    if raw_csv_path and os.path.exists(raw_csv_path):
        try:
            recs = _read_csv_records(raw_csv_path)
            recs = [r for r in recs if start_year <= r["year"] <= end_year]
            if recs:
                return recs
        except Exception:
            pass
    return _ar1_series(start_year, end_year, mu=mean, phi=phi, sigma=sigma, x0=x0)
