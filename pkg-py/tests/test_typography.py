from __future__ import annotations

from urllib.parse import unquote

import pytest
from brand_yaml import read_brand_yaml
from brand_yaml.color import BrandColor
from brand_yaml.typography import (
    BrandTypography,
    BrandTypographyBase,
    BrandTypographyFontBunny,
    BrandTypographyFontFiles,
    BrandTypographyFontFilesPath,
    BrandTypographyFontGoogle,
    BrandTypographyGoogleFontsApi,
    BrandTypographyHeadings,
    BrandTypographyLink,
    BrandTypographyMonospace,
    BrandTypographyMonospaceBlock,
    BrandTypographyMonospaceInline,
)
from syrupy.extensions.json import JSONSnapshotExtension
from utils import path_examples, pydantic_data_from_json


@pytest.fixture
def snapshot_json(snapshot):
    return snapshot.use_extension(JSONSnapshotExtension)


@pytest.mark.parametrize(
    "path, fmt",
    [
        ("my-font.otf", "opentype"),
        ("my-font.ttf", "truetype"),
        ("my-font.woff", "woff"),
        ("my-font.woff2", "woff2"),
    ],
)
def test_brand_typography_font_file_format(path, fmt):
    font = BrandTypographyFontFilesPath(path=path)

    assert font.path == path
    assert font.format == fmt


def test_brand_typography_font_file_weight():
    args = {
        "path": "my-font.otf",
    }

    with pytest.raises(ValueError):
        BrandTypographyFontFilesPath.model_validate(
            {**args, "weight": "invalid"}
        )

    with pytest.raises(ValueError):
        BrandTypographyFontFilesPath.model_validate({**args, "weight": 999})

    with pytest.raises(ValueError):
        BrandTypographyFontFilesPath.model_validate({**args, "weight": 150})

    with pytest.raises(ValueError):
        BrandTypographyFontFilesPath.model_validate({**args, "weight": 0})

    assert (
        BrandTypographyFontFilesPath.model_validate(
            {**args, "weight": 100}
        ).weight
        == 100
    )
    assert (
        BrandTypographyFontFilesPath.model_validate(
            {**args, "weight": "thin"}
        ).weight
        == 100
    )
    assert (
        BrandTypographyFontFilesPath.model_validate(
            {**args, "weight": "semi-bold"}
        ).weight
        == 600
    )
    assert (
        BrandTypographyFontFilesPath.model_validate(
            {**args, "weight": "bold"}
        ).weight
        == "bold"
    )
    assert (
        BrandTypographyFontFilesPath.model_validate(
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

    # TODO: Compare directly with brand-yaml spec
    assert base_fields == {
        "family",
        "weight",
        "size",
        "line_height",
        "color",
    }


def test_brand_typography_fields_headings():
    headings_fields = set(BrandTypographyHeadings.model_fields.keys())

    # TODO: Compare directly with brand-yaml spec
    assert headings_fields == {
        "family",
        "weight",
        "style",
        "line_height",
        "color",
    }


def test_brand_typography_fields_monospace():
    fields = set(BrandTypographyMonospace.model_fields.keys())

    # TODO: Compare directly with brand-yaml spec
    assert fields == {"family", "weight", "size"}


def test_brand_typography_fields_monospace_inline():
    fields = set(BrandTypographyMonospaceInline.model_fields.keys())

    # TODO: Compare directly with brand-yaml spec
    assert fields == {
        "family",
        "weight",
        "size",
        "color",
        "background_color",
    }


def test_brand_typography_fields_monospace_block():
    fields = set(BrandTypographyMonospaceBlock.model_fields.keys())

    # TODO: Compare directly with brand-yaml spec
    assert fields == {
        "family",
        "weight",
        "size",
        "line_height",
        "color",
        "background_color",
    }


def test_brand_typography_fields_link():
    fields = set(BrandTypographyLink.model_fields.keys())

    # TODO: Compare directly with brand-yaml spec
    assert fields == {
        "weight",
        "decoration",
        "color",
        "background_color",
    }


def test_brand_typography_font_bunny():
    bf = BrandTypography.model_validate(
        {
            "fonts": [
                {
                    "source": "bunny",
                    "family": "Kode Mono",
                    "weight": [400, 500, 600, 700],
                    "style": "normal",
                }
            ]
        }
    )

    assert len(bf.fonts) == 1
    assert isinstance(bf.fonts[0], BrandTypographyFontBunny)
    assert isinstance(bf.fonts[0], BrandTypographyGoogleFontsApi)


def test_brand_typography_font_google_import_url():
    bg = BrandTypography.model_validate(
        {
            "fonts": [
                {
                    "source": "google",
                    "family": "Open Sans",
                    "weight": [700, 400],
                    "style": ["italic", "normal"],
                }
            ]
        }
    )

    assert len(bg.fonts) == 1
    assert isinstance(bg.fonts[0], BrandTypographyFontGoogle)
    assert (
        unquote(bg.fonts[0].import_url())
        == "https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,400;0,700;1,400;1,700&display=auto"
    )


def test_brand_typography_font_bunny_import_url():
    bg = BrandTypography.model_validate(
        {
            "fonts": [
                {
                    "source": "bunny",
                    "family": "Open Sans",
                    "weight": [700, 400],
                    "style": ["italic", "normal"],
                }
            ]
        }
    )

    assert len(bg.fonts) == 1
    assert isinstance(bg.fonts[0], BrandTypographyFontBunny)
    assert (
        unquote(bg.fonts[0].import_url())
        == "https://fonts.bunny.net/css?family=Open+Sans:400,400i,700,700i&display=auto"
    )


def test_brand_typography_ex_simple(snapshot_json):
    brand = read_brand_yaml(path_examples("brand-typography-simple.yml"))

    assert isinstance(brand.typography, BrandTypography)

    assert isinstance(brand.typography.fonts, list)
    assert len(brand.typography.fonts) == 3
    assert [f.family for f in brand.typography.fonts] == [
        "Open Sans",
        "Roboto Slab",
        "Fira Code",
    ]
    assert [f.source for f in brand.typography.fonts] == ["google"] * 3

    assert brand.typography.link is None
    assert isinstance(brand.typography.base, BrandTypographyBase)
    assert isinstance(brand.typography.headings, BrandTypographyHeadings)
    assert isinstance(brand.typography.monospace, BrandTypographyMonospace)
    assert isinstance(
        brand.typography.monospace_inline, BrandTypographyMonospace
    )
    assert isinstance(
        brand.typography.monospace_block, BrandTypographyMonospace
    )
    assert isinstance(
        brand.typography.monospace_inline, BrandTypographyMonospaceInline
    )
    assert isinstance(
        brand.typography.monospace_block, BrandTypographyMonospaceBlock
    )

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_typography_ex_fonts(snapshot_json):
    brand = read_brand_yaml(path_examples("brand-typography-fonts.yml"))

    assert isinstance(brand.typography, BrandTypography)
    assert len(brand.typography.fonts) == 4

    # Local Font Files
    local_font = brand.typography.fonts[0]
    assert isinstance(local_font, BrandTypographyFontFiles)
    assert local_font.source == "file"
    assert local_font.family == "Open Sans"
    for i, font in enumerate(local_font.files):
        assert isinstance(font, BrandTypographyFontFilesPath)
        assert str(font.path).startswith("Open-Sans")
        assert str(font.path).endswith(".ttf")
        assert font.format == "truetype"
        assert font.weight == ["bold", "normal"][i]
        assert font.style == ["normal", "italic"][i]

    # Online Font Files
    online_font = brand.typography.fonts[1]
    assert isinstance(online_font, BrandTypographyFontFiles)
    assert online_font.source == "file"
    assert online_font.family == "Closed Sans"
    for i, font in enumerate(online_font.files):
        assert isinstance(font, BrandTypographyFontFilesPath)
        assert str(font.path).startswith("https://")
        assert str(font.path).endswith(".woff2")
        assert font.format == "woff2"
        assert font.weight == ["bold", "normal"][i]
        assert font.style == ["normal", "italic"][i]

    # Google Fonts
    google_font = brand.typography.fonts[2]
    assert isinstance(google_font, BrandTypographyFontGoogle)
    assert google_font.family == "Roboto Slab"
    assert google_font.weight == 600
    assert google_font.style == "normal"
    assert google_font.display == "block"

    # Bunny Fonts
    bunny_font = brand.typography.fonts[3]
    assert isinstance(bunny_font, BrandTypographyFontBunny)
    assert bunny_font.family == "Fira Code"

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_typography_ex_color(snapshot_json):
    brand = read_brand_yaml(path_examples("brand-typography-color.yml"))

    assert isinstance(brand.typography, BrandTypography)
    assert isinstance(brand.color, BrandColor)

    t = brand.typography
    color = brand.color
    assert color.palette is not None

    assert isinstance(t.base, BrandTypographyBase)
    assert t.base.color == color.foreground

    assert isinstance(t.headings, BrandTypographyHeadings)
    assert t.headings.color == color.primary

    assert isinstance(t.monospace_inline, BrandTypographyMonospaceInline)
    assert t.monospace_inline.color == color.background
    assert t.monospace_inline.background_color == color.palette["red"]

    assert isinstance(t.monospace_block, BrandTypographyMonospaceBlock)
    assert t.monospace_block.color == color.foreground
    assert t.monospace_block.background_color == color.background

    assert isinstance(t.link, BrandTypographyLink)
    assert t.link.color == color.palette["red"]

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_typography_ex_minimal(snapshot_json):
    brand = read_brand_yaml(path_examples("brand-typography-minimal.yml"))

    assert isinstance(brand.typography, BrandTypography)

    assert isinstance(brand.typography.fonts, list)
    assert len(brand.typography.fonts) == 3
    assert brand.typography.fonts[0].source == "file"
    assert brand.typography.fonts[0].files == []

    assert isinstance(brand.typography.fonts[1], BrandTypographyFontGoogle)
    assert brand.typography.fonts[1].family == "Roboto Slab"

    assert isinstance(brand.typography.fonts[2], BrandTypographyFontGoogle)
    assert brand.typography.fonts[2].family == "Fira Code"

    assert snapshot_json == pydantic_data_from_json(brand)
