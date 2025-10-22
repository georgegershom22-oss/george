from typing import List, Dict
import random

random.seed(17)

SECTORS: List[str] = [
    "Agriculture", "Manufacturing", "Construction", "Trade", "Information & Communication",
    "Finance & Insurance", "Real Estate", "Transportation & Storage", "Education",
    "Health & Social Services", "Utilities", "Public Administration"
]


def generate_sectoral_growth(start_year: int, end_year: int) -> List[Dict]:
    years = list(range(start_year, end_year + 1))
    rows: List[Dict] = []
    for sector in SECTORS:
        baseline = random.gauss(2.5, 1.0)
        for year in years:
            shock = 0.0
            if year in {2016}:
                shock += random.gauss(-2.5, 0.7)
            if year in {2020}:
                shock += random.gauss(-3.0, 1.0)
            recovery = 0.0
            if year in {2017, 2021}:
                recovery += random.gauss(1.2, 0.6)
            trend = 0.05 * (year - years[0])
            noise = random.gauss(0.0, 1.0)
            growth = baseline + shock + recovery + trend + noise
            rows.append({
                "year": year,
                "sector": sector,
                "growth_rate_pct": round(float(growth), 2)
            })
    rows.sort(key=lambda r: (r["year"], r["sector"]))
    return rows
