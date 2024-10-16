from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote

import pytest
from brand_yaml import Brand, read_brand_yaml
from brand_yaml.color import BrandColor
from brand_yaml.file import FileLocationLocal
from brand_yaml.typography import (
    BrandTypography,
    BrandTypographyBase,
    BrandTypographyFontBunny,
    BrandTypographyFontFiles,
    BrandTypographyFontFilesPath,
    BrandTypographyFontFileWeight,
    BrandTypographyFontGoogle,
    BrandTypographyGoogleFontsApi,
    BrandTypographyGoogleFontsWeightRange,
    BrandTypographyHeadings,
    BrandTypographyLink,
    BrandTypographyMonospace,
    BrandTypographyMonospaceBlock,
    BrandTypographyMonospaceInline,
    BrandUnsupportedFontFileFormat,
    validate_font_weight,
)
from syrupy.extensions.json import JSONSnapshotExtension
from utils import path_examples, pydantic_data_from_json, set_env_var


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

    assert str(font.path.root) == path
    assert font.format == fmt


def test_validate_font_weight():
    assert validate_font_weight(None) == "auto"
    assert validate_font_weight("auto") == "auto"
    assert validate_font_weight("normal") == "normal"
    assert validate_font_weight("bold") == "bold"

    assert validate_font_weight("thin") == 100
    assert validate_font_weight("semi-bold") == 600

    with pytest.raises(ValueError):
        validate_font_weight("invalid")

    with pytest.raises(ValueError):
        validate_font_weight([100, 200])

    with pytest.raises(ValueError):
        # Auto is only allowed as a single value
        validate_font_weight(["auto", "normal"])


def test_brand_typography_font_file_weight():
    with pytest.raises(ValueError):
        BrandTypographyFontFileWeight.model_validate("invalid")

    with pytest.raises(ValueError):
        BrandTypographyFontFileWeight.model_validate(999)

    with pytest.raises(ValueError):
        BrandTypographyFontFileWeight.model_validate(150)

    with pytest.raises(ValueError):
        BrandTypographyFontFileWeight.model_validate(0)

    assert BrandTypographyFontFileWeight.model_validate(100).root == 100
    assert BrandTypographyFontFileWeight.model_validate("thin").root == 100
    assert BrandTypographyFontFileWeight.model_validate("semi-bold").root == 600
    assert BrandTypographyFontFileWeight.model_validate("bold").root == "bold"
    assert (
        BrandTypographyFontFileWeight.model_validate("normal").root == "normal"
    )
    assert BrandTypographyFontFileWeight.model_validate("auto").root == "auto"

    assert BrandTypographyFontFileWeight.model_validate([100, 200]).root == (
        100,
        200,
    )
    thin_bold = BrandTypographyFontFileWeight.model_validate(["thin", "bold"])
    assert thin_bold.root == (100, "bold")
    assert str(thin_bold) == "100 700"

    with pytest.raises(ValueError):
        BrandTypographyFontFileWeight.model_validate(["thin", "auto"])


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


def test_brand_typography_font_local_no_files():
    """
    A local font file source without any files can be used to signal that the
    system font should be used. We expect no errors and for the font-inclusion
    CSS to be empty.
    """
    bf = BrandTypography.model_validate(
        {
            "fonts": [{"source": "file", "family": "Arial"}],
            "base": "Arial",
        }
    )

    assert isinstance(bf.fonts, list)
    assert isinstance(bf.fonts[0], BrandTypographyFontFiles)
    assert isinstance(bf.base, BrandTypographyBase)
    assert bf.base.family == "Arial"
    assert bf.css_include_fonts() == ""


@pytest.mark.parametrize("font_file", ["arial", "arial.pdf"])
def test_brand_typography_font_file_ext_error(font_file):
    with pytest.raises(ValueError):
        BrandTypography.model_validate(
            {
                "fonts": [
                    {
                        "source": "file",
                        "family": "Arial",
                        "files": [{"path": font_file}],
                    }
                ]
            }
        )

    with pytest.raises(ValueError):
        BrandTypographyFontFilesPath.model_validate({"path": font_file})

    with pytest.raises(BrandUnsupportedFontFileFormat):
        bt = BrandTypographyFontFilesPath.model_validate({"path": "arial.ttf"})

        assert isinstance(bt.path, FileLocationLocal)
        bt.path.root = Path("arial")
        bt.format


@pytest.mark.parametrize("font_file", ["arial.svg", "arial.eot", "arial.ttc"])
def test_brand_typography_font_file_errors(font_file):
    with pytest.raises(BrandUnsupportedFontFileFormat):
        bt = BrandTypography.model_validate(
            {
                "fonts": [
                    {
                        "source": "file",
                        "family": "Arial",
                        "files": [{"path": font_file}],
                    }
                ]
            }
        )

        assert isinstance(bt.fonts[0], BrandTypographyFontFiles)
        assert isinstance(bt.fonts[0].files, list)
        assert isinstance(bt.fonts[0].files[0], BrandTypographyFontFilesPath)
        bt.fonts[0].files[0].format


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
        unquote(bg.fonts[0].to_import_url())
        == "https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,400;0,700;1,400;1,700&display=auto"
    )

    bg_no_weight = BrandTypography.model_validate(
        {
            "fonts": [
                {
                    "source": "google",
                    "family": "Open Sans",
                    "weight": [],
                    "style": ["italic", "normal"],
                }
            ]
        }
    )

    assert len(bg_no_weight.fonts) == 1
    assert isinstance(bg_no_weight.fonts[0], BrandTypographyFontGoogle)
    assert (
        unquote(bg_no_weight.fonts[0].to_import_url())
        == "https://fonts.googleapis.com/css2?family=Open+Sans:ital@0;1&display=auto"
    )

    bg_no_ital = BrandTypography.model_validate(
        {
            "fonts": [
                {
                    "source": "google",
                    "family": "Open Sans",
                    "weight": [700, 400],
                    "style": [],
                }
            ]
        }
    )

    assert len(bg_no_ital.fonts) == 1
    assert isinstance(bg_no_ital.fonts[0], BrandTypographyFontGoogle)
    assert (
        unquote(bg_no_ital.fonts[0].to_import_url())
        == "https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=auto"
    )

    bg_no_axes = BrandTypography.model_validate(
        {
            "fonts": [
                {
                    "source": "google",
                    "family": "Open Sans",
                    "weight": [],
                    "style": [],
                }
            ]
        }
    )

    assert len(bg_no_axes.fonts) == 1
    assert isinstance(bg_no_axes.fonts[0], BrandTypographyFontGoogle)
    assert (
        unquote(bg_no_axes.fonts[0].to_import_url())
        == "https://fonts.googleapis.com/css2?family=Open+Sans&display=auto"
    )


def test_brand_typography_font_google_weight_range_import_url():
    bg = BrandTypography.model_validate(
        {
            "fonts": [
                {
                    "source": "google",
                    "family": "Open Sans",
                    "weight": "400..700",
                    "style": ["italic", "normal"],
                }
            ]
        }
    )

    assert isinstance(bg.fonts[0], BrandTypographyFontGoogle)
    assert isinstance(bg.fonts[0].weight, BrandTypographyGoogleFontsWeightRange)
    assert (
        unquote(bg.fonts[0].to_import_url())
        == "https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,400..700;1,400..700&display=auto"
    )


def test_brand_typography_font_google_weight_range_error():
    with pytest.raises(ValueError):
        BrandTypography.model_validate(
            {
                "fonts": [
                    {
                        "source": "google",
                        "family": "Open Sans",
                        "weight": "400..700..900",
                        "style": ["italic", "normal"],
                    }
                ]
            }
        )


def test_brand_typography_font_bunny_import_url():
    bf = BrandTypography.model_validate(
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

    assert len(bf.fonts) == 1
    assert isinstance(bf.fonts[0], BrandTypographyFontBunny)
    assert (
        unquote(bf.fonts[0].to_import_url())
        == "https://fonts.bunny.net/css?family=Open+Sans:400,400i,700,700i&display=auto"
    )

    bf_no_weight = BrandTypography.model_validate(
        {
            "fonts": [
                {
                    "source": "bunny",
                    "family": "Open Sans",
                    "weight": [],
                    "style": ["italic", "normal"],
                }
            ]
        }
    )

    assert len(bf_no_weight.fonts) == 1
    assert isinstance(bf_no_weight.fonts[0], BrandTypographyFontBunny)
    assert (
        unquote(bf_no_weight.fonts[0].to_import_url())
        == "https://fonts.bunny.net/css?family=Open+Sans:regular,italic&display=auto"
    )

    bf_no_ital = BrandTypography.model_validate(
        {
            "fonts": [
                {
                    "source": "bunny",
                    "family": "Open Sans",
                    "weight": [700, 400],
                    "style": [],
                }
            ]
        }
    )

    assert len(bf_no_ital.fonts) == 1
    assert isinstance(bf_no_ital.fonts[0], BrandTypographyFontBunny)
    assert (
        unquote(bf_no_ital.fonts[0].to_import_url())
        == "https://fonts.bunny.net/css?family=Open+Sans:400,700&display=auto"
    )

    bf_no_axes = BrandTypography.model_validate(
        {
            "fonts": [
                {
                    "source": "bunny",
                    "family": "Open Sans",
                    "weight": [],
                    "style": [],
                }
            ]
        }
    )

    assert len(bf_no_axes.fonts) == 1
    assert isinstance(bf_no_axes.fonts[0], BrandTypographyFontBunny)
    assert (
        unquote(bf_no_axes.fonts[0].to_import_url())
        == "https://fonts.bunny.net/css?family=Open+Sans&display=auto"
    )


def test_brand_typography_ex_simple_system(snapshot_json):
    brand = read_brand_yaml(path_examples("brand-typography-simple.yml"))

    assert isinstance(brand.typography, BrandTypography)

    assert isinstance(brand.typography.fonts, list)
    assert len(brand.typography.fonts) == 3
    assert [f.family for f in brand.typography.fonts] == [
        "Open Sans",
        "Roboto Slab",
        "Fira Code",
    ]
    assert [f.source for f in brand.typography.fonts] == ["system"] * 3

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_typography_ex_simple_google(snapshot_json):
    with set_env_var("BRAND_YAML_DEFAULT_FONT_SOURCE", "google"):
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
        assert "OpenSans" in str(font.path.root)
        assert str(font.path.root).endswith(".ttf")
        assert font.format == "truetype"
        assert isinstance(font.weight, BrandTypographyFontFileWeight)
        assert str(font.weight) == ["auto", "auto"][i]
        assert font.style == ["normal", "italic"][i]

    # Online Font Files
    online_font = brand.typography.fonts[1]
    assert isinstance(online_font, BrandTypographyFontFiles)
    assert online_font.source == "file"
    assert online_font.family == "Closed Sans"
    for i, font in enumerate(online_font.files):
        assert isinstance(font, BrandTypographyFontFilesPath)
        assert str(font.path.root).startswith("https://")
        assert str(font.path.root).endswith(".woff2")
        assert font.format == "woff2"
        assert str(font.weight) == ["bold", "auto"][i]
        assert font.style == ["normal", "italic"][i]

    # Google Fonts
    google_font = brand.typography.fonts[2]
    assert isinstance(google_font, BrandTypographyFontGoogle)
    assert google_font.family == "Roboto Slab"
    assert isinstance(google_font.weight, BrandTypographyGoogleFontsWeightRange)
    assert str(google_font.weight) == "600..900"
    assert google_font.weight.to_url_list() == ["600..900"]
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
    with set_env_var("BRAND_YAML_DEFAULT_FONT_SOURCE", "google"):
        brand = read_brand_yaml(path_examples("brand-typography-minimal.yml"))

    assert isinstance(brand.typography, BrandTypography)

    assert isinstance(brand.typography.fonts, list)
    assert len(brand.typography.fonts) == 3
    assert isinstance(brand.typography.fonts[0], BrandTypographyFontGoogle)
    assert brand.typography.fonts[0].family == "Open Sans"

    assert isinstance(brand.typography.fonts[1], BrandTypographyFontGoogle)
    assert brand.typography.fonts[1].family == "Roboto Slab"

    assert isinstance(brand.typography.fonts[2], BrandTypographyFontGoogle)
    assert brand.typography.fonts[2].family == "Fira Code"

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_typography_ex_minimal_mixed_source(snapshot_json):
    with set_env_var("BRAND_YAML_DEFAULT_FONT_SOURCE", "google"):
        brand = read_brand_yaml(
            path_examples("brand-typography-minimal-system.yml")
        )

    assert isinstance(brand.typography, BrandTypography)

    assert isinstance(brand.typography.fonts, list)
    assert len(brand.typography.fonts) == 3
    assert brand.typography.fonts[0].source == "system"
    assert brand.typography.fonts[0].family == "Open Sans"

    assert isinstance(brand.typography.fonts[1], BrandTypographyFontGoogle)
    assert brand.typography.fonts[1].family == "Roboto Slab"

    assert isinstance(brand.typography.fonts[2], BrandTypographyFontGoogle)
    assert brand.typography.fonts[2].family == "Fira Code"

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_typography_css_fonts(snapshot):
    brand = read_brand_yaml(path_examples("brand-typography-fonts.yml"))

    assert isinstance(brand.typography, BrandTypography)
    assert snapshot == brand.typography.css_include_fonts()


def test_brand_typography_css_fonts_local(snapshot):
    fw = BrandTypographyFontFileWeight.model_validate("400..800")
    assert str(fw) == "400 800"
    assert fw.model_dump() == "400..800"
    assert fw.to_str_url() == "400..800"

    with pytest.raises(ValueError):
        BrandTypographyFontFileWeight.model_validate("400..600..900")

    fp = BrandTypographyFontFilesPath.model_validate(
        {"path": "OpenSans-Variable.ttf", "weight": "400..800"}
    )
    assert fp.to_css() == "\n".join(
        [
            "font-weight: 400 800;",
            "font-style: normal;",
            "src: url('OpenSans-Variable.ttf') format('truetype');",
        ]
    )

    brand = Brand.from_yaml_str("""
    typography:
      fonts:
        - family: Open Sans
          source: file
          files:
            - path: OpenSans-Variable.ttf
              weight: 400..800
              style: italic
        - family: Roboto
          source: google
          weight: 200..500
    """)

    assert isinstance(brand.typography, BrandTypography)
    assert snapshot == brand.typography.css_include_fonts()


def test_brand_typography_google_fonts_weight_range(snapshot):
    fw = BrandTypographyGoogleFontsWeightRange.model_validate("600..800")
    assert fw.root == [600, 800]
    assert str(fw) == "600..800"
    assert fw.model_dump() == "600..800"
    assert fw.to_url_list() == ["600..800"]

    fw = BrandTypographyGoogleFontsWeightRange.model_validate(["thin", "bold"])
    assert fw.root == [100, 700]

    with pytest.raises(ValueError):
        BrandTypographyGoogleFontsWeightRange.model_validate("600..800..123")

    with pytest.raises(ValueError):
        BrandTypographyGoogleFontsWeightRange.model_validate([200, 400, 600])


def test_brand_typography_undefined_colors():
    fixtures = Path(__file__).parent / "fixtures" / "typography-undefined-color"

    with pytest.raises(ValueError, match="typography.base.color"):
        read_brand_yaml(fixtures / "undefined-base-color.yml")

    with pytest.raises(
        ValueError, match="typography.monospace.background-color"
    ):
        read_brand_yaml(fixtures / "undefined-monospace-background-color.yml")

    with pytest.raises(ValueError, match="typography.headings.color"):
        read_brand_yaml(fixtures / "undefined-headings-color.yml")

    brand = read_brand_yaml(fixtures / "undefined-palette-headings-color.yml")
    assert isinstance(brand.typography, BrandTypography)
    assert isinstance(brand.typography.headings, BrandTypographyHeadings)
    assert brand.typography.headings.color == "orange"
