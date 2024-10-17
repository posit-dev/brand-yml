from __future__ import annotations

import copy
from pathlib import Path

import pytest
from brand_yml.file import FileLocation, FileLocationLocal, FileLocationUrl


def test_file_requires_extension():
    with pytest.raises(ValueError):
        FileLocationLocal.model_validate("fancy-logo")

    with pytest.raises(ValueError):
        FileLocationUrl.model_validate("https://example.com/my-font")

    local = FileLocationLocal.model_validate("fancy-logo.png")
    assert isinstance(local, FileLocation)
    assert isinstance(local, FileLocationLocal)
    assert str(local) == "fancy-logo.png"

    url = FileLocationUrl.model_validate("https://example.com/my-font.ttf")
    assert isinstance(url, FileLocationUrl)
    assert isinstance(url, FileLocation)
    assert str(url) == "https://example.com/my-font.ttf"


def test_local_file_path_resolution():
    local = FileLocationLocal.model_validate("fancy-logo.png")
    assert isinstance(local, FileLocation)
    assert isinstance(local, FileLocationLocal)
    assert str(local) == "fancy-logo.png"
    assert local.relative() == Path("fancy-logo.png")

    local.set_root_dir(Path(__file__).parent)
    assert local.absolute() == Path(__file__).parent / "fancy-logo.png"

    assert not local.exists()

    with pytest.raises(FileNotFoundError):
        local.validate_exists()


def test_local_file_cannot_be_absolute():
    with pytest.raises(ValueError, match="file:///"):
        FileLocationLocal.model_validate("/fancy-logo.png")

    with pytest.raises(ValueError, match="file:///"):
        FileLocationLocal.model_validate("~/fancy-logo.png")


def test_local_files_retain_root_after_copy():
    local = FileLocationLocal.model_validate("fancy-logo.png")
    local.set_root_dir(Path(__file__).parent)

    local_copy = copy.copy(local)
    assert local_copy.absolute() == local.absolute()
    assert local_copy.model_dump() == local.model_dump()

    local_deep = copy.deepcopy(local)
    assert local_deep.absolute() == local.absolute()
    assert local_deep.model_dump() == local.model_dump()
