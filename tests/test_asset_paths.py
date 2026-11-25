# Copyright (c) 2026, gw.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Asset selection must preserve the current model and support newly restored directories."""

import json

import pytest

from go2_locomotion.assets import paths


@pytest.fixture
def asset_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "GO2_ASSET_DIR", tmp_path)
    monkeypatch.setattr(paths, "GO2_MANIFEST_PATH", tmp_path / "asset_manifest.json")
    monkeypatch.setattr(paths, "LEGACY_GO2_USD_PATH", tmp_path / "existing" / "go2.usd")
    return tmp_path


def test_existing_installation_is_preserved(asset_dir):
    assert paths.get_go2_usd_path() == asset_dir / "existing" / "go2.usd"
    assert not paths.GO2_MANIFEST_PATH.exists()


def test_restored_directory_does_not_depend_on_original_uuid(asset_dir):
    paths.GO2_MANIFEST_PATH.write_text(json.dumps({"usd_path": "new_download/1/go2.usd"}), encoding="utf-8")
    assert paths.get_go2_usd_path() == asset_dir / "new_download" / "1" / "go2.usd"


@pytest.mark.parametrize("usd_path", ["../outside/go2.usd", "/tmp/go2.usd"])
def test_manifest_cannot_select_a_file_outside_asset_directory(asset_dir, usd_path):
    paths.GO2_MANIFEST_PATH.write_text(json.dumps({"usd_path": usd_path}), encoding="utf-8")
    with pytest.raises(ValueError, match="must be relative"):
        paths.get_go2_usd_path()
