from __future__ import annotations

from pathlib import Path

import pytest
from brand_yaml.file import FileLocation, FileLocationLocal, FileLocationUrl


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

    local.make_absolute(Path(__file__).parent)
    assert str(local) == str(Path(__file__).parent / "fancy-logo.png")

    with pytest.raises(FileNotFoundError):
        local.validate_path_exists()
