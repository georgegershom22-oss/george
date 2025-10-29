from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any

import h5py
import numpy as np


def save_sample_h5(out_path: str | Path, sample_idx: int, meta: Dict[str, Any], fields: Dict[str, np.ndarray]) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(out_path, "w") as h5:
        # Attributes
        for k, v in meta.get("attributes", {}).items():
            h5.attrs[k] = v

        # Operating conditions
        grp_in = h5.create_group("input")
        grp_op = grp_in.create_group("operating")
        for k, v in meta["operating"].items():
            grp_op.attrs[k] = v

        # Geometry
        grp_geo = grp_in.create_group("geometry")
        for k, v in meta["geometry"].items():
            grp_geo.attrs[k] = v

        # Materials per layer
        grp_mat = grp_in.create_group("materials")
        for layer_name, props in meta["materials"].items():
            grp_layer = grp_mat.create_group(layer_name)
            for k, v in props.items():
                grp_layer.attrs[k] = v

        # Output fields
        grp_out = h5.create_group("output")
        for name, arr in fields.items():
            grp_out.create_dataset(name, data=arr, compression="gzip", compression_opts=4)

        # Index
        h5.attrs["sample_index"] = int(sample_idx)


def write_manifest(manifest_path: str | Path, manifest: Dict[str, Any]) -> None:
    p = Path(manifest_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(manifest, f, indent=2)
