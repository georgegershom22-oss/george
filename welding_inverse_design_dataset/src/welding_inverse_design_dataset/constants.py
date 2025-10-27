from typing import Dict, List

TECHNIQUES: List[str] = ["USW", "Laser", "RSW"]

SURFACE_FINISHES: List[str] = [
    "as_rolled",
    "brushed",
    "electroplated_Ni",
    "electroplated_Ag",
    "tinned_Sn",
    "anodized",
    "oxidized",
]

COATINGS: List[str] = ["none", "Ni", "Ag", "Sn"]

SURFACE_FINISH_RA_UM: Dict[str, float] = {
    "as_rolled": 1.6,
    "brushed": 1.2,
    "electroplated_Ni": 0.6,
    "electroplated_Ag": 0.5,
    "tinned_Sn": 0.8,
    "anodized": 0.9,
    "oxidized": 2.4,
}

COATING_ABSORPTION_BOOST: Dict[str, float] = {
    # multiplicative boost to absorption for laser, capped later
    "none": 1.0,
    "Ni": 1.25,
    "Ag": 1.35,
    "Sn": 1.15,
}
