# Copyright (c) 2026, gw.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Restore missing Go2 USD assets, or inspect the existing local model without simulation."""

import argparse
import hashlib
import json
from pathlib import Path

from go2_locomotion.assets.paths import GO2_ASSET_DIR, GO2_MANIFEST_PATH, GO2_SOURCE_URL, get_go2_usd_path


def inspect_usd(usd_path: Path) -> dict[str, str]:
    """Check USD dependencies and composition, returning hashes of the local dependency files."""
    from pxr import Sdf, Usd, UsdUtils

    if not usd_path.is_file():
        raise FileNotFoundError(f"Go2 USD is missing: {usd_path}. Run scripts/restore_assets.py without --check.")
    layers, assets, unresolved = UsdUtils.ComputeAllDependencies(Sdf.AssetPath(str(usd_path)))
    # OmniPBR is a renderer-resolved MDL module, not a missing USD geometry file.
    # Keep this exception narrow: unresolved USD files and other assets remain errors.
    unresolved_files = [path for path in unresolved if path != "OmniPBR.mdl"]
    if unresolved_files:
        raise RuntimeError(f"Unresolved USD dependencies: {unresolved_files}")
    if "OmniPBR.mdl" in unresolved:
        print("Renderer module OmniPBR.mdl: left to the MDL renderer; material rendering is not validated.")
    stage = Usd.Stage.Open(str(usd_path))
    if stage is None or not stage.GetDefaultPrim() or stage.GetCompositionErrors():
        raise RuntimeError(f"Go2 USD composition is invalid: {usd_path}")

    dependencies = {usd_path.resolve(), *(Path(layer.realPath).resolve() for layer in layers)}
    dependencies.update(Path(asset).resolve() for asset in assets)
    hashes = {}
    for path in sorted(dependencies):
        relative_path = path.relative_to(GO2_ASSET_DIR.resolve())
        hashes[relative_path.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Check the active local model without downloading or writing."
    )
    args = parser.parse_args(argv)

    usd_path = get_go2_usd_path()
    if args.check or usd_path.is_file():
        hashes = inspect_usd(usd_path)
        if GO2_MANIFEST_PATH.is_file():
            recorded = json.loads(GO2_MANIFEST_PATH.read_text(encoding="utf-8"))["sha256"]
            if hashes != recorded:
                raise RuntimeError("Go2 assets differ from the restoration manifest. Review any local model edits.")
        print(f"Go2 USD: {usd_path}\nValidated local dependency files: {len(hashes)}")
        return

    # Import the downloader only for an explicit restoration of missing files.
    from isaaclab.utils.assets import retrieve_file_path

    GO2_ASSET_DIR.mkdir(parents=True, exist_ok=True)
    usd_path = Path(retrieve_file_path(GO2_SOURCE_URL, download_dir=str(GO2_ASSET_DIR))).resolve()
    hashes = inspect_usd(usd_path)
    manifest = {
        "source_url": GO2_SOURCE_URL,
        "usd_path": usd_path.relative_to(GO2_ASSET_DIR.resolve()).as_posix(),
        "sha256": hashes,
    }
    temporary_path = GO2_MANIFEST_PATH.with_suffix(".json.tmp")
    temporary_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    temporary_path.replace(GO2_MANIFEST_PATH)
    print(f"Restored Go2 USD: {usd_path}\nManifest: {GO2_MANIFEST_PATH}")


if __name__ == "__main__":
    main()
