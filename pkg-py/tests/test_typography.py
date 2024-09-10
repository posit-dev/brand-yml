from __future__ import annotations

import pytest

from brand_yaml.typography import (
    BrandTypography,
    BrandTypographyBase,
    BrandTypographyFontFile,
    BrandTypographyHeadings,
    BrandTypographyLink,
    BrandTypographyMonospace,
    BrandTypographyMonospaceBlock,
    BrandTypographyMonospaceInline,
)


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


def test_brand_typography_monospace():
    bt = BrandTypography.model_validate(
        {
            "monospace": {"family": "Fira Code", "size": "1.2rem"},
            "monospace-inline": {"size": "0.9rem"},
            "monospace-block": {
                "family": "Menlo",
            },
        }
    )

    assert bt.monospace is not None
    assert bt.monospace.family == "Fira Code"
    assert bt.monospace.size == "1.2rem"

    assert bt.monospace_inline is not None
    assert bt.monospace_inline.family == "Fira Code"  # inherits family
    assert bt.monospace_inline.size == "0.9rem"  # overrides size

    assert bt.monospace_block is not None
    assert bt.monospace_block.family == "Menlo"  # overrides family
    assert bt.monospace_block.size == "1.2rem"  # inherits size


def test_brand_typography_fields_base():
    base_fields = set(BrandTypographyBase.model_fields.keys())

    assert base_fields == {
        "family",
        "weight",
        "style",
        "size",
        "line_height",
        "color",
        "background_color",
    }


def test_brand_typography_fields_headings():
    headings_fields = set(BrandTypographyHeadings.model_fields.keys())

    assert headings_fields == {
        "family",
        "weight",
        "style",
        "line_height",
        "color",
        "background_color",
    }


def test_brand_typography_fields_monospace():
    fields = set(BrandTypographyMonospace.model_fields.keys())

    assert fields == {"family", "weight", "style", "size"}


def test_brand_typography_fields_monospace_inline():
    fields = set(BrandTypographyMonospaceInline.model_fields.keys())

    assert fields == {
        "family",
        "weight",
        "style",
        "size",
        "color",
        "background_color",
    }


def test_brand_typography_fields_monospace_block():
    fields = set(BrandTypographyMonospaceBlock.model_fields.keys())

    assert fields == {
        "family",
        "weight",
        "style",
        "size",
        "line_height",
        "color",
        "background_color",
    }


def test_brand_typography_fields_link():
    fields = set(BrandTypographyLink.model_fields.keys())

    assert fields == {
        "weight",
        "decoration",
        "color",
        "background_color",
    }
