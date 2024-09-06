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
    font = BrandTypographyFontFile(source=source, family="My Font")

    assert font.source == source
    assert font.format == fmt


def test_brand_typography_font_file_format_ignored():
    # ignores user-provided formats, uses `source` field
    BrandTypographyFontFile(
        source="my-font.otf",
        family="My Font",
        format="invalid",
    )


def test_brand_typography_font_file_weight():
    args = {"source": "my-font.otf", "family": "My Font"}

    with pytest.raises(ValueError):
        BrandTypographyFontFile(**args, weight="invalid")

    with pytest.raises(ValueError):
        BrandTypographyFontFile(**args, weight=999)

    with pytest.raises(ValueError):
        BrandTypographyFontFile(**args, weight=150)

    with pytest.raises(ValueError):
        BrandTypographyFontFile(**args, weight=0)

    assert BrandTypographyFontFile(**args, weight=100).weight == 100
    assert BrandTypographyFontFile(**args, weight="thin").weight == 100
    assert BrandTypographyFontFile(**args, weight="semi-bold").weight == 600
    assert BrandTypographyFontFile(**args, weight="bold").weight == "bold"
    assert BrandTypographyFontFile(**args, weight="normal").weight == "normal"
