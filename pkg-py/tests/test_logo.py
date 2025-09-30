from __future__ import annotations

from pathlib import Path

import pytest
from brand_yml import Brand
from brand_yml._defs import BrandLightDark
from brand_yml._use_logo import BrandLogoMissingError
from brand_yml.file import FileLocation, FileLocationLocal
from brand_yml.logo import (
    BrandLogo,
    BrandLogoResource,
    BrandLogoResourceLightDark,
)
from syrupy.extensions.json import JSONSnapshotExtension
from utils import path_examples, pydantic_data_from_json


@pytest.fixture
def snapshot_json(snapshot):
    return snapshot.use_extension(JSONSnapshotExtension)


def test_brand_logo_single():
    brand = Brand.from_yaml(path_examples("brand-logo-single.yml"))

    assert isinstance(brand.logo, BrandLogoResource)
    assert isinstance(brand.logo.path, FileLocationLocal)
    assert str(brand.logo.path) == "posit.png"


def test_brand_logo_errors():
    with pytest.raises(ValueError):
        BrandLogo.model_validate("foo")

    with pytest.raises(ValueError):
        BrandLogo.model_validate({"images": "foo"})

    with pytest.raises(ValueError):
        BrandLogo.model_validate({"images": {"light": 1234}})


def test_brand_logo_images_accept_paths():
    BrandLogo.model_validate({"images": {"cat": Path("cat.jpg")}})


def test_brand_logo_ex_simple(snapshot_json):
    brand = Brand.from_yaml(path_examples("brand-logo-simple.yml"))

    assert isinstance(brand.logo, BrandLogo)

    assert isinstance(brand.logo.small, BrandLogoResource)
    assert isinstance(brand.logo.small.path, FileLocation)
    assert str(brand.logo.small.path) == "logos/pandas/pandas_mark.svg"

    assert isinstance(brand.logo.medium, BrandLogoResource)
    assert isinstance(brand.logo.medium.path, FileLocation)
    assert str(brand.logo.medium.path) == "logos/pandas/pandas_secondary.svg"

    assert isinstance(brand.logo.large, BrandLogoResource)
    assert isinstance(brand.logo.large.path, FileLocation)
    assert str(brand.logo.large.path) == "logos/pandas/pandas.svg"

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_logo_ex_light_dark(snapshot_json):
    brand = Brand.from_yaml(path_examples("brand-logo-light-dark.yml"))

    assert isinstance(brand.logo, BrandLogo)
    assert isinstance(brand.logo.small, BrandLogoResource)
    assert isinstance(brand.logo.small.path, FileLocationLocal)
    assert str(brand.logo.small.path) == "logos/pandas/pandas_mark.svg"

    assert isinstance(brand.logo.medium, BrandLightDark)
    assert isinstance(brand.logo.medium.light, BrandLogoResource)
    assert isinstance(brand.logo.medium.light.path, FileLocationLocal)
    assert (
        str(brand.logo.medium.light.path) == "logos/pandas/pandas_secondary.svg"
    )
    assert isinstance(brand.logo.medium.dark, BrandLogoResource)
    assert isinstance(brand.logo.medium.dark.path, FileLocationLocal)
    assert (
        str(brand.logo.medium.dark.path)
        == "logos/pandas/pandas_secondary_white.svg"
    )

    assert isinstance(brand.logo.large, BrandLogoResource)
    assert isinstance(brand.logo.large.path, FileLocationLocal)
    assert str(brand.logo.large.path) == "logos/pandas/pandas.svg"

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_logo_ex_full(snapshot_json):
    brand = Brand.from_yaml(path_examples("brand-logo-full.yml"))

    assert isinstance(brand.logo, BrandLogo)
    assert isinstance(brand.logo.images, dict)
    assert isinstance(brand.logo.small, BrandLogoResource)
    assert isinstance(brand.logo.small.path, FileLocationLocal)
    assert brand.logo.small == brand.logo.images["mark"]

    assert isinstance(brand.logo.medium, BrandLightDark)
    assert isinstance(brand.logo.medium.light, BrandLogoResource)
    assert isinstance(brand.logo.medium.light.path, FileLocationLocal)
    assert brand.logo.medium.light.path.root == Path(
        "logos/pandas/pandas_secondary.svg"
    )
    assert isinstance(brand.logo.medium.dark, BrandLogoResource)
    assert brand.logo.medium.dark == brand.logo.images["secondary-white"]

    assert isinstance(brand.logo.large, BrandLogoResource)
    assert isinstance(brand.logo.large.path, FileLocationLocal)
    assert brand.logo.large == brand.logo.images["pandas"]

    ## THIS IS NOT CURRENTLY SUPPORTED
    ## We handle internal references in before model validation which is too
    ## early for the updated field value replacement. We could revisit this if
    ## we change how FileLocations are handled.
    # replace small with new value from "logo.images"
    # brand.logo.small = "mark-white"  # type: ignore
    # brand.model_rebuild()
    # assert isinstance(brand.logo.small, FileLocation)
    # assert brand.logo.small == brand.logo.images["mark-white"]

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_logo_resource_images_simple():
    brand = Brand.from_yaml_str("""
    logo:
      images:
        logo: brand-yaml.png
      small: logo
    """)

    # logo.images.* are promoted to BrandLogoResource
    assert isinstance(brand.logo, BrandLogo)
    assert isinstance(brand.logo.images, dict)
    assert "logo" in brand.logo.images
    assert isinstance(brand.logo.images["logo"], BrandLogoResource)
    assert isinstance(brand.logo.images["logo"].path, FileLocationLocal)
    assert brand.logo.images["logo"].alt is None
    assert str(brand.logo.images["logo"].path.relative()) == "brand-yaml.png"

    # and are used directly by logo.*
    assert isinstance(brand.logo.small, BrandLogoResource)
    assert brand.logo.small == brand.logo.images["logo"]


def test_brand_logo_resource_images_with_alt():
    brand = Brand.from_yaml_str("""
    logo:
      images:
        logo:
          path: brand-yaml.png
          alt: "Brand YAML Logo"
      small: logo
    """)

    assert isinstance(brand.logo, BrandLogo)
    assert isinstance(brand.logo.images, dict)
    assert "logo" in brand.logo.images
    assert isinstance(brand.logo.images["logo"], BrandLogoResource)
    assert isinstance(brand.logo.images["logo"].path, FileLocationLocal)
    assert isinstance(brand.logo.images["logo"].alt, str)
    assert str(brand.logo.images["logo"].path.relative()) == "brand-yaml.png"

    # and are used directly by logo.*
    assert isinstance(brand.logo.small, BrandLogoResource)
    assert brand.logo.small == brand.logo.images["logo"]
    assert brand.logo.small.alt == "Brand YAML Logo"


def test_brand_logo_resource_direct_with_alt():
    brand = Brand.from_yaml_str("""
    logo:
      small:
        path: brand-yaml.png
        alt: "Brand YAML Logo"
    """)

    assert isinstance(brand.logo, BrandLogo)

    # and are used directly by logo.*
    assert isinstance(brand.logo.small, BrandLogoResource)
    assert str(brand.logo.small.path) == "brand-yaml.png"
    assert brand.logo.small.alt == "Brand YAML Logo"


def test_brand_logo_ex_full_alt(snapshot_json):
    brand = Brand.from_yaml(path_examples("brand-logo-full-alt.yml"))

    assert snapshot_json == pydantic_data_from_json(brand)


# Tests for Brand.use_logo() method


def test_use_logo_no_logo():
    """Test use_logo() when no logo is defined"""
    brand = Brand.from_yaml_str("meta: {name: Test}")

    # Should return None when no logo exists and not required
    assert brand.use_logo("small") is None
    assert brand.use_logo("medium") is None
    assert brand.use_logo("large") is None

    # Should raise error when required
    with pytest.raises(
        BrandLogoMissingError, match="brand.logo.small is required"
    ):
        brand.use_logo("small", required=True)

    with pytest.raises(
        BrandLogoMissingError, match="brand.logo.custom is required for testing"
    ):
        brand.use_logo("custom", required="for testing")


def test_use_logo_single_resource():
    """Test use_logo() with a single logo resource"""
    brand = Brand.from_yaml_str("""
    logo:
      path: single-logo.png
      alt: Single Logo
    """)

    # Single logo now DOES support size-based access
    small = brand.use_logo("small")
    assert isinstance(small, BrandLogoResource)
    assert str(small.path) == "single-logo.png"
    assert small.alt == "Single Logo"

    medium = brand.use_logo("medium")
    assert isinstance(medium, BrandLogoResource)
    assert str(medium.path) == "single-logo.png"
    assert medium.alt == "Single Logo"

    large = brand.use_logo("large")
    assert isinstance(large, BrandLogoResource)
    assert str(large.path) == "single-logo.png"
    assert large.alt == "Single Logo"

    # Smallest/largest should also work
    smallest = brand.use_logo("smallest")
    assert isinstance(smallest, BrandLogoResource)
    assert str(smallest.path) == "single-logo.png"

    largest = brand.use_logo("largest")
    assert isinstance(largest, BrandLogoResource)
    assert str(largest.path) == "single-logo.png"

    # Named access still doesn't work for single resource
    assert brand.use_logo("custom-name", required=False) is None

    with pytest.raises(
        BrandLogoMissingError,
        match="brand.logo.images\\['custom-name'\\] is required",
    ):
        brand.use_logo("custom-name")

    with pytest.raises(
        BrandLogoMissingError,
        match="brand.logo.images\\['custom-name'\\] is required",
    ):
        brand.use_logo("custom-name", required=True)


def test_use_logo_from_images():
    """Test use_logo() with images dictionary"""
    brand = Brand.from_yaml_str("""
    logo:
      images:
        custom-logo: logo.png
        another-logo:
          path: another.png
          alt: Another Logo
      small: custom-logo
    """)

    # Access by image name
    logo = brand.use_logo("custom-logo")
    assert isinstance(logo, BrandLogoResource)
    assert str(logo.path) == "logo.png"
    assert logo.alt is None

    logo2 = brand.use_logo("another-logo")
    assert isinstance(logo2, BrandLogoResource)
    assert str(logo2.path) == "another.png"
    assert logo2.alt == "Another Logo"

    # Access by size
    small_logo = brand.use_logo("small")
    assert isinstance(small_logo, BrandLogoResource)
    assert str(small_logo.path) == "logo.png"

    # Non-existent image
    assert brand.use_logo("nonexistent", required=False) is None

    with pytest.raises(
        BrandLogoMissingError,
        match="brand.logo.images\\['nonexistent'\\] is required",
    ):
        brand.use_logo("nonexistent")

    with pytest.raises(
        BrandLogoMissingError,
        match="brand.logo.images\\['nonexistent'\\] is required",
    ):
        brand.use_logo("nonexistent", required=True)


def test_use_logo_smallest_largest():
    """Test smallest/largest convenience options"""
    brand = Brand.from_yaml_str("""
    logo:
      small: small.png
      large: large.png
    """)

    # smallest should return small (first available)
    smallest = brand.use_logo("smallest")
    assert isinstance(smallest, BrandLogoResource)
    assert str(smallest.path) == "small.png"

    # largest should return large (last available)
    largest = brand.use_logo("largest")
    assert isinstance(largest, BrandLogoResource)
    assert str(largest.path) == "large.png"

    # Test with all sizes
    brand_full = Brand.from_yaml_str("""
    logo:
      small: small.png
      medium: medium.png
      large: large.png
    """)

    smallest_full = brand_full.use_logo("smallest")
    assert isinstance(smallest_full, BrandLogoResource)
    assert str(smallest_full.path) == "small.png"

    largest_full = brand_full.use_logo("largest")
    assert isinstance(largest_full, BrandLogoResource)
    assert str(largest_full.path) == "large.png"


def test_use_logo_variant_auto_single():
    """Test variant='auto' with single logo resources"""
    brand = Brand.from_yaml_str("""
    logo:
      small: small.png
      medium:
        light: medium-light.png
        dark: medium-dark.png
    """)

    # Auto with single resource returns the resource
    small = brand.use_logo("small", variant="auto")
    assert isinstance(small, BrandLogoResource)
    assert str(small.path) == "small.png"

    # Auto with light/dark returns the light/dark container
    medium = brand.use_logo("medium", variant="auto")
    assert isinstance(medium, BrandLogoResourceLightDark)
    assert isinstance(medium.light, BrandLogoResource)
    assert isinstance(medium.dark, BrandLogoResource)
    assert str(medium.light.path) == "medium-light.png"
    assert str(medium.dark.path) == "medium-dark.png"


def test_use_logo_variant_auto_partial():
    """Test variant='auto' with partial light/dark"""
    brand = Brand.from_yaml_str("""
    logo:
      small:
        light: small-light.png
      medium:
        dark: medium-dark.png
    """)

    # Auto with only light returns light
    small = brand.use_logo("small", variant="auto")
    assert isinstance(small, BrandLogoResource)
    assert str(small.path) == "small-light.png"

    # Auto with only dark returns dark
    medium = brand.use_logo("medium", variant="auto")
    assert isinstance(medium, BrandLogoResource)
    assert str(medium.path) == "medium-dark.png"


def test_use_logo_variant_specific():
    """Test specific variant selection"""
    brand = Brand.from_yaml_str("""
    logo:
      small: small.png
      medium:
        light: medium-light.png
        dark: medium-dark.png
    """)

    # Light variant from light/dark
    medium_light = brand.use_logo("medium", variant="light")
    assert isinstance(medium_light, BrandLogoResource)
    assert str(medium_light.path) == "medium-light.png"

    # Dark variant from light/dark
    medium_dark = brand.use_logo("medium", variant="dark")
    assert isinstance(medium_dark, BrandLogoResource)
    assert str(medium_dark.path) == "medium-dark.png"

    # Light variant with fallback to single
    small_light = brand.use_logo("small", variant="light")
    assert isinstance(small_light, BrandLogoResource)
    assert str(small_light.path) == "small.png"

    # Light variant without fallback
    assert (
        brand.use_logo("small", variant="light", allow_fallback=False) is None
    )


def test_use_logo_variant_light_dark():
    """Test variant=['light', 'dark'] behavior"""
    brand = Brand.from_yaml_str("""
    logo:
      small: small.png
      medium:
        light: medium-light.png
        dark: medium-dark.png
    """)

    # Light/dark from existing light/dark
    medium_both = brand.use_logo("medium", variant="light-dark")
    assert isinstance(medium_both, BrandLogoResourceLightDark)
    assert medium_both.light is not None
    assert medium_both.dark is not None
    assert str(medium_both.light.path) == "medium-light.png"
    assert str(medium_both.dark.path) == "medium-dark.png"

    # Light/dark with fallback promotion
    small_both = brand.use_logo("small", variant="light-dark")
    assert isinstance(small_both, BrandLogoResourceLightDark)
    assert small_both.light is not None
    assert small_both.dark is not None
    assert str(small_both.light.path) == "small.png"
    assert str(small_both.dark.path) == "small.png"

    # Light/dark without fallback
    assert (
        brand.use_logo("small", variant="light-dark", allow_fallback=False)
        is None
    )


def test_use_logo_error_cases():
    """Test error conditions"""
    brand = Brand.from_yaml_str("""
    logo:
      small: small.png
      medium:
        light: medium-light.png
    """)

    # Invalid variant
    with pytest.raises(ValueError, match="variant must be"):
        brand.use_logo("small", variant="invalid")  # type: ignore

    with pytest.raises(ValueError, match="variant must be"):
        brand.use_logo("small", variant=["light"])  # type: ignore

    # Missing variant without fallback
    with pytest.raises(
        BrandLogoMissingError, match="brand.logo.medium.dark is required"
    ):
        brand.use_logo(
            "medium", variant="dark", allow_fallback=False, required=True
        )

    # Missing light/dark variants without fallback
    with pytest.raises(
        BrandLogoMissingError,
        match="brand.logo.small with light/dark variants",
    ):
        brand.use_logo(
            "small",
            variant="light-dark",
            allow_fallback=False,
            required=True,
        )


def test_use_logo_attrs():
    """Test attribute attachment"""
    brand = Brand.from_yaml_str("""
    logo:
      small:
        path: small.png
        attrs:
          class: existing-class
    """)

    # Basic attrs
    logo = brand.use_logo("small", width="100", height="50")
    assert isinstance(logo, BrandLogoResource)
    assert logo.attrs is not None
    assert logo.attrs["class"] == "existing-class"
    assert logo.attrs["width"] == "100"
    assert logo.attrs["height"] == "50"

    # Attrs are merged, not replaced
    logo2 = brand.use_logo("small", class_="new-class")
    assert isinstance(logo2, BrandLogoResource)
    assert logo2.attrs is not None
    assert logo2.attrs["class"] == "existing-class new-class"


def test_use_logo_path_resolution():
    """Test path resolution to absolute paths"""
    # Create a temporary brand file to test path resolution
    brand = Brand.from_yaml_str(
        """
    logo:
      small: small.png
    """,
        path="/test/path/_brand.yml",
    )

    logo = brand.use_logo("small")
    assert isinstance(logo, BrandLogoResource)
    # Path should be resolved relative to the brand file location
    assert isinstance(logo.path, FileLocationLocal)


def test_use_logo_formatting_methods():
    """Test formatting methods on returned logo resources"""
    brand = Brand.from_yaml_str("""
    logo:
      small: small.png
      medium:
        light: medium-light.png
        dark: medium-dark.png
    """)

    # Single resource formatting
    logo = brand.use_logo("small")
    assert hasattr(logo, "to_html")
    assert hasattr(logo, "to_markdown")
    assert hasattr(logo, "to_str")
    assert hasattr(logo, "tagify")

    # Light/dark resource formatting
    logo_ld = brand.use_logo("medium")
    assert hasattr(logo_ld, "to_html")
    assert hasattr(logo_ld, "to_markdown")
    assert hasattr(logo_ld, "to_str")
    assert hasattr(logo_ld, "tagify")
