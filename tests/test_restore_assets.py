# Copyright (c) 2026, gw.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Exercise restoration with temporary USD files; never download or edit the real robot model."""

import importlib.util
import json
from pathlib import Path

import pytest

from go2_locomotion.assets import paths


@pytest.fixture
def restoration(tmp_path, monkeypatch):
    script = Path(__file__).resolve().parents[1] / "scripts" / "restore_assets.py"
    spec = importlib.util.spec_from_file_location("restore_assets", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(paths, "GO2_ASSET_DIR", tmp_path)
    monkeypatch.setattr(paths, "GO2_MANIFEST_PATH", tmp_path / "asset_manifest.json")
    monkeypatch.setattr(paths, "LEGACY_GO2_USD_PATH", tmp_path / "existing" / "go2.usd")
    monkeypatch.setattr(module, "GO2_ASSET_DIR", tmp_path)
    monkeypatch.setattr(module, "GO2_MANIFEST_PATH", paths.GO2_MANIFEST_PATH)
    return module


def write_usd(path, references=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '#usda 1.0\n( defaultPrim = "Go2" )\ndef Xform "Go2"'
        + (f" ( prepend references = @{references}@ )" if references else "")
        + " {}\n",
        encoding="utf-8",
    )


def test_check_missing_assets_does_not_write(restoration):
    with pytest.raises(FileNotFoundError, match="Go2 USD is missing"):
        restoration.main(["--check"])
    assert not paths.GO2_MANIFEST_PATH.exists()


def test_existing_model_is_checked_without_replacement(restoration, monkeypatch):
    import isaaclab.utils.assets as downloader

    def unexpected_download(*args, **kwargs):
        pytest.fail("An existing model must not be downloaded again.")

    monkeypatch.setattr(downloader, "retrieve_file_path", unexpected_download)
    write_usd(paths.LEGACY_GO2_USD_PATH)
    before = paths.LEGACY_GO2_USD_PATH.read_bytes()
    restoration.main([])
    assert paths.LEGACY_GO2_USD_PATH.read_bytes() == before
    assert not paths.GO2_MANIFEST_PATH.exists()


def test_restoration_records_dependencies_and_detects_later_edits(restoration, tmp_path, monkeypatch):
    import isaaclab.utils.assets as downloader

    root = tmp_path / "new_download" / "1" / "go2.usda"
    child = tmp_path / "new_download" / "2" / "base.usda"
    write_usd(child)
    write_usd(root, "../2/base.usda")
    monkeypatch.setattr(downloader, "retrieve_file_path", lambda *args, **kwargs: str(root))

    restoration.main([])
    manifest_bytes = paths.GO2_MANIFEST_PATH.read_bytes()
    manifest = json.loads(manifest_bytes)
    assert paths.get_go2_usd_path() == root
    assert set(manifest["sha256"]) == {"new_download/1/go2.usda", "new_download/2/base.usda"}

    restoration.main(["--check"])
    assert paths.GO2_MANIFEST_PATH.read_bytes() == manifest_bytes
    child.write_text(child.read_text(encoding="utf-8") + "# research edit\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="differ from the restoration manifest"):
        restoration.main(["--check"])
    assert paths.GO2_MANIFEST_PATH.read_bytes() == manifest_bytes


def test_broken_dependencies_do_not_publish_a_manifest(restoration, tmp_path, monkeypatch):
    import isaaclab.utils.assets as downloader

    root = tmp_path / "new_download" / "go2.usda"
    write_usd(root, "missing.usda")
    monkeypatch.setattr(downloader, "retrieve_file_path", lambda *args, **kwargs: str(root))
    with pytest.raises(RuntimeError, match="Unresolved USD dependencies"):
        restoration.main([])
    assert not paths.GO2_MANIFEST_PATH.exists()


@pytest.mark.parametrize("module_name", ["OmniPBR.mdl", "missing_material.mdl"])
def test_only_known_renderer_module_is_exempted(restoration, tmp_path, module_name):
    root = tmp_path / "go2.usda"
    root.write_text(
        '#usda 1.0\n( defaultPrim = "Go2" )\ndef Xform "Go2" {\n'
        f"    custom asset rendererModule = @{module_name}@\n"
        "}\n",
        encoding="utf-8",
    )
    if module_name == "OmniPBR.mdl":
        assert set(restoration.inspect_usd(root)) == {"go2.usda"}
    else:
        with pytest.raises(RuntimeError, match="Unresolved USD dependencies"):
            restoration.inspect_usd(root)
