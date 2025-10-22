from typing import List, Dict
import math
import random

random.seed(123)


def logistic_curve(t: float, L: float = 100.0, k: float = 0.3, x0: float = 2015.0) -> float:
    return L / (1.0 + math.exp(-k * (t - x0)))


def generate_mobile_money_adoption(start_year: int, end_year: int) -> List[Dict]:
    rows: List[Dict] = []
    for year in range(start_year, end_year + 1):
        base = logistic_curve(year, L=85.0, k=0.35, x0=2018.0)
        noise = random.gauss(0.0, 3.0)
        adoption = max(2.0, min(95.0, base + noise))
        rows.append({"year": year, "mobile_money_adoption_pct": round(adoption, 2)})
    return rows


def generate_itu_idi(start_year: int, end_year: int) -> List[Dict]:
    rows: List[Dict] = []
    for year in range(start_year, end_year + 1):
        trend = 2.5 + 0.25 * (year - start_year)
        noise = random.gauss(0.0, 0.3)
        idx = max(0.0, min(10.0, trend + noise))
        rows.append({"year": year, "itu_idi_index": round(idx, 2)})
    return rows
