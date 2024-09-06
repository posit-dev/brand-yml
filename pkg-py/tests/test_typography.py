from __future__ import annotations

import pytest

from brand_yaml.typography import BrandTypographyFontFile


@pytest.mark.parametrize(
    "source, fmt",
    [
        ("my-font.otf", "opentype"),
        ("my-font.ttf", "truetype"),
        ("my-font.woff", "woff"),
        ("my-font.woff2", "woff2"),
    ],
)
def test_brand_typography_font_file_format(source, fmt):
    font = BrandTypographyFontFile(source=source)

    assert font.source == source
    assert font.format == fmt


def test_brand_typography_font_file_format_ignored():
    # ignores user-provided formats, uses `source` field
    BrandTypographyFontFile(source="my-font.otf", format="invalid")


def test_brand_typography_font_file_weight():
    src = "my-font.otf"

    with pytest.raises(ValueError):
        BrandTypographyFontFile(source=src, weight="invalid")

    with pytest.raises(ValueError):
        BrandTypographyFontFile(source=src, weight=999)

    with pytest.raises(ValueError):
        BrandTypographyFontFile(source=src, weight=150)

    with pytest.raises(ValueError):
        BrandTypographyFontFile(source=src, weight=0)

    assert BrandTypographyFontFile(source=src, weight=100).weight == 100
    assert BrandTypographyFontFile(source=src, weight="thin").weight == 100
    assert BrandTypographyFontFile(source=src, weight="semi-bold").weight == 600
    assert BrandTypographyFontFile(source=src, weight="bold").weight == "bold"
    assert (
        BrandTypographyFontFile(source=src, weight="normal").weight == "normal"
    )
