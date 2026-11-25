# Copyright (c) 2026, gw.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Local Go2 asset paths without simulation initialization or automatic downloads."""

import json
from pathlib import Path

GO2_ASSET_DIR = Path(__file__).resolve().parent / "data" / "go2"
GO2_MANIFEST_PATH = GO2_ASSET_DIR / "asset_manifest.json"
GO2_SOURCE_URL = (
    "https://omniverse-content-production.s3-us-west-2.amazonaws.com"
    "/Assets/Isaac/6.2/Isaac/IsaacLab/Robots/Unitree/Go2/go2.usd"
)
LEGACY_GO2_USD_PATH = GO2_ASSET_DIR / "isaaclab_usd_6b05af4d27784e9fa10be1e289491635" / "1" / "go2.usd"


def get_go2_usd_path() -> Path:
    """Use an explicitly restored asset, falling back to the existing local installation."""
    if not GO2_MANIFEST_PATH.is_file():
        return LEGACY_GO2_USD_PATH

    manifest = json.loads(GO2_MANIFEST_PATH.read_text(encoding="utf-8"))
    relative_path = Path(manifest["usd_path"])
    usd_path = (GO2_ASSET_DIR / relative_path).resolve()
    if relative_path.is_absolute() or not usd_path.is_relative_to(GO2_ASSET_DIR.resolve()):
        raise ValueError(f"Go2 USD path must be relative to {GO2_ASSET_DIR}: {relative_path}")
    return usd_path
