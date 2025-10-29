from __future__ import annotations
import os
import h5py
import numpy as np
import pandas as pd
from typing import Dict, Any


def write_run_h5(out_dir: str, run_id: int, params: Dict[str, Any], fields: Dict[str, np.ndarray]) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"run_{run_id:05d}.h5")
    with h5py.File(path, "w") as f:
        # Inputs group
        g_in = f.create_group("inputs")
        for k, v in params.items():
            g_in.attrs[k] = v
        # Fields group
        g = f.create_group("fields")
        for name, arr in fields.items():
            g.create_dataset(name, data=arr, compression="gzip", compression_opts=4)
    return path


def append_metadata_csv(csv_path: str, run_id: int, file_path: str, params: Dict[str, Any]) -> None:
    row = {"run_id": run_id, "file": os.path.relpath(file_path, os.path.dirname(csv_path))}
    row.update(params)
    df = pd.DataFrame([row])
    if not os.path.exists(csv_path):
        df.to_csv(csv_path, index=False)
    else:
        df.to_csv(csv_path, mode="a", header=False, index=False)
