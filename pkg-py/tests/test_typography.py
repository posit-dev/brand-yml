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
    BrandTypographyFontFile.model_validate(
        {"source": "my-font.otf", "family": "My Font"}
    )


def test_brand_typography_font_file_weight():
    args = {"source": "my-font.otf", "family": "My Font"}

    with pytest.raises(ValueError):
        BrandTypographyFontFile.model_validate({**args, "weight": "invalid"})

    with pytest.raises(ValueError):
        BrandTypographyFontFile.model_validate({**args, "weight": 999})

    with pytest.raises(ValueError):
        BrandTypographyFontFile.model_validate({**args, "weight": 150})

    with pytest.raises(ValueError):
        BrandTypographyFontFile.model_validate({**args, "weight": 0})

    assert (
        BrandTypographyFontFile.model_validate({**args, "weight": 100}).weight
        == 100
    )
    assert (
        BrandTypographyFontFile.model_validate(
            {**args, "weight": "thin"}
        ).weight
        == 100
    )
    assert (
        BrandTypographyFontFile.model_validate(
            {**args, "weight": "semi-bold"}
        ).weight
        == 600
    )
    assert (
        BrandTypographyFontFile.model_validate(
            {**args, "weight": "bold"}
        ).weight
        == "bold"
    )
    assert (
        BrandTypographyFontFile.model_validate(
            {**args, "weight": "normal"}
        ).weight
        == "normal"
    )
