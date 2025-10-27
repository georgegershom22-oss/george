#!/usr/bin/env python
from __future__ import annotations

import argparse
import os
import zipfile
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="Package welding dataset into a zip archive")
    parser.add_argument("--src", type=str, default="data")
    parser.add_argument("--outdir", type=str, default="data/artifacts")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_zip = os.path.join(args.outdir, f"welding_dataset_{ts}.zip")

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(args.src):
            for fn in files:
                # avoid packaging artifacts inside artifacts
                if root.startswith(args.outdir):
                    continue
                path = os.path.join(root, fn)
                arcname = os.path.relpath(path, start=args.src)
                zf.write(path, arcname)

    print(f"Packaged dataset to {out_zip}")


if __name__ == "__main__":
    main()
