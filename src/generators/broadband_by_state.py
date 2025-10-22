from typing import Optional, List, Dict
import random
from src.utils.states import NIGERIAN_STATES, STATE_TO_REGION

random.seed(7)


def generate_broadband_by_state(year: int, base_penetration_national: float = 45.0,
                                 regional_bias: Optional[dict] = None) -> List[Dict]:
    if regional_bias is None:
        regional_bias = {
            "South West": 1.15,
            "South South": 1.05,
            "South East": 1.00,
            "North Central": 0.95,
            "North West": 0.85,
            "North East": 0.82,
        }
    rows: List[Dict] = []
    for state in NIGERIAN_STATES:
        region = STATE_TO_REGION[state]
        bias = regional_bias.get(region, 1.0)
        urban_bonus = 1.20 if state in {"Lagos", "FCT", "Rivers"} else 1.0
        noise = random.gauss(0.0, 4.0)
        penetration = max(5.0, min(100.0, base_penetration_national * bias * urban_bonus + noise))
        rows.append({
            "year": year,
            "state": state,
            "region": region,
            "broadband_penetration_pct": round(float(penetration), 2),
        })
    # Sort by region, state
    rows.sort(key=lambda r: (r["region"], r["state"]))
    return rows
