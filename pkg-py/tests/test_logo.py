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


class TestBrandLogoBasics:
    """Test basic logo loading and validation"""

    def test_brand_logo_single(self):
        brand = Brand.from_yaml(path_examples("brand-logo-single.yml"))

        assert isinstance(brand.logo, BrandLogoResource)
        assert isinstance(brand.logo.path, FileLocationLocal)
        assert str(brand.logo.path) == "posit.png"

    def test_brand_logo_errors(self):
        with pytest.raises(ValueError):
            BrandLogo.model_validate("foo")

        with pytest.raises(ValueError):
            BrandLogo.model_validate({"images": "foo"})

        with pytest.raises(ValueError):
            BrandLogo.model_validate({"images": {"light": 1234}})

    def test_brand_logo_images_accept_paths(self):
        BrandLogo.model_validate({"images": {"cat": Path("cat.jpg")}})


class TestBrandLogoExamples:
    """Test example brand logo files"""

    def test_brand_logo_ex_simple(self, snapshot_json):
        brand = Brand.from_yaml(path_examples("brand-logo-simple.yml"))

        assert isinstance(brand.logo, BrandLogo)

        assert isinstance(brand.logo.small, BrandLogoResource)
        assert isinstance(brand.logo.small.path, FileLocation)
        assert str(brand.logo.small.path) == "logos/pandas/pandas_mark.svg"

        assert isinstance(brand.logo.medium, BrandLogoResource)
        assert isinstance(brand.logo.medium.path, FileLocation)
        assert (
            str(brand.logo.medium.path) == "logos/pandas/pandas_secondary.svg"
        )

        assert isinstance(brand.logo.large, BrandLogoResource)
        assert isinstance(brand.logo.large.path, FileLocation)
        assert str(brand.logo.large.path) == "logos/pandas/pandas.svg"

        assert snapshot_json == pydantic_data_from_json(brand)

    def test_brand_logo_ex_light_dark(self, snapshot_json):
        brand = Brand.from_yaml(path_examples("brand-logo-light-dark.yml"))

        assert isinstance(brand.logo, BrandLogo)
        assert isinstance(brand.logo.small, BrandLogoResource)
        assert isinstance(brand.logo.small.path, FileLocationLocal)
        assert str(brand.logo.small.path) == "logos/pandas/pandas_mark.svg"

        assert isinstance(brand.logo.medium, BrandLightDark)
        assert isinstance(brand.logo.medium.light, BrandLogoResource)
        assert isinstance(brand.logo.medium.light.path, FileLocationLocal)
        assert (
            str(brand.logo.medium.light.path)
            == "logos/pandas/pandas_secondary.svg"
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

    def test_brand_logo_ex_full(self, snapshot_json):
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

    def test_brand_logo_ex_full_alt(self, snapshot_json):
        brand = Brand.from_yaml(path_examples("brand-logo-full-alt.yml"))

        assert snapshot_json == pydantic_data_from_json(brand)


class TestBrandLogoResourceImages:
    """Test logo resource images dictionary"""

    @pytest.fixture
    def brand_simple_images(self):
        """Brand with simple images dictionary"""
        return Brand.from_yaml_str("""
        logo:
          images:
            logo: brand-yaml.png
          small: logo
        """)

    @pytest.fixture
    def brand_images_with_alt(self):
        """Brand with images that have alt text"""
        return Brand.from_yaml_str("""
        logo:
          images:
            logo:
              path: brand-yaml.png
              alt: "Brand YAML Logo"
          small: logo
        """)

    @pytest.fixture
    def brand_direct_with_alt(self):
        """Brand with direct logo definition with alt text"""
        return Brand.from_yaml_str("""
        logo:
          small:
            path: brand-yaml.png
            alt: "Brand YAML Logo"
        """)

    def test_brand_logo_resource_images_simple(self, brand_simple_images):
        brand = brand_simple_images

        # logo.images.* are promoted to BrandLogoResource
        assert isinstance(brand.logo, BrandLogo)
        assert isinstance(brand.logo.images, dict)
        assert "logo" in brand.logo.images
        assert isinstance(brand.logo.images["logo"], BrandLogoResource)
        assert isinstance(brand.logo.images["logo"].path, FileLocationLocal)
        assert brand.logo.images["logo"].alt is None
        assert (
            str(brand.logo.images["logo"].path.relative()) == "brand-yaml.png"
        )

        # and are used directly by logo.*
        assert isinstance(brand.logo.small, BrandLogoResource)
        assert brand.logo.small == brand.logo.images["logo"]

    def test_brand_logo_resource_images_with_alt(self, brand_images_with_alt):
        brand = brand_images_with_alt

        assert isinstance(brand.logo, BrandLogo)
        assert isinstance(brand.logo.images, dict)
        assert "logo" in brand.logo.images
        assert isinstance(brand.logo.images["logo"], BrandLogoResource)
        assert isinstance(brand.logo.images["logo"].path, FileLocationLocal)
        assert isinstance(brand.logo.images["logo"].alt, str)
        assert (
            str(brand.logo.images["logo"].path.relative()) == "brand-yaml.png"
        )

        # and are used directly by logo.*
        assert isinstance(brand.logo.small, BrandLogoResource)
        assert brand.logo.small == brand.logo.images["logo"]
        assert brand.logo.small.alt == "Brand YAML Logo"

    def test_brand_logo_resource_direct_with_alt(self, brand_direct_with_alt):
        brand = brand_direct_with_alt

        assert isinstance(brand.logo, BrandLogo)

        # and are used directly by logo.*
        assert isinstance(brand.logo.small, BrandLogoResource)
        assert str(brand.logo.small.path) == "brand-yaml.png"
        assert brand.logo.small.alt == "Brand YAML Logo"


class TestUseLogoNoLogo:
    """Test use_logo() when no logo is defined"""

    @pytest.fixture
    def brand_no_logo(self):
        """Brand without any logo"""
        return Brand.from_yaml_str("meta: {name: Test}")

    def test_use_logo_no_logo_returns_none(self, brand_no_logo):
        """Test use_logo() returns None when no logo exists and not required"""
        assert brand_no_logo.use_logo("small") is None
        assert brand_no_logo.use_logo("medium") is None
        assert brand_no_logo.use_logo("large") is None

    def test_use_logo_no_logo_raises_when_required(self, brand_no_logo):
        """Test use_logo() raises error when required"""
        with pytest.raises(
            BrandLogoMissingError, match="brand.logo.small is required"
        ):
            brand_no_logo.use_logo("small", required=True)

        with pytest.raises(
            BrandLogoMissingError,
            match="brand.logo.custom is required for testing",
        ):
            brand_no_logo.use_logo("custom", required="for testing")


class TestUseLogoSingleResource:
    """Test use_logo() with a single logo resource"""

    @pytest.fixture
    def brand_single_logo(self):
        """Brand with a single logo resource"""
        return Brand.from_yaml_str("""
        logo:
          path: single-logo.png
          alt: Single Logo
        """)

    def test_use_logo_single_resource_sizes(self, brand_single_logo):
        """Test use_logo() with size-based access on single resource"""
        # Single logo now DOES support size-based access
        small = brand_single_logo.use_logo("small")
        assert isinstance(small, BrandLogoResource)
        assert str(small.path) == "single-logo.png"
        assert small.alt == "Single Logo"

        medium = brand_single_logo.use_logo("medium")
        assert isinstance(medium, BrandLogoResource)
        assert str(medium.path) == "single-logo.png"
        assert medium.alt == "Single Logo"

        large = brand_single_logo.use_logo("large")
        assert isinstance(large, BrandLogoResource)
        assert str(large.path) == "single-logo.png"
        assert large.alt == "Single Logo"

    def test_use_logo_single_resource_smallest_largest(self, brand_single_logo):
        """Test smallest/largest access on single resource"""
        smallest = brand_single_logo.use_logo("smallest")
        assert isinstance(smallest, BrandLogoResource)
        assert str(smallest.path) == "single-logo.png"

        largest = brand_single_logo.use_logo("largest")
        assert isinstance(largest, BrandLogoResource)
        assert str(largest.path) == "single-logo.png"

    def test_use_logo_single_resource_named_access_fails(
        self, brand_single_logo
    ):
        """Test that named access doesn't work for single resource"""
        assert brand_single_logo.use_logo("custom-name", required=False) is None

        with pytest.raises(
            BrandLogoMissingError,
            match="brand.logo.images\\['custom-name'\\] is required",
        ):
            brand_single_logo.use_logo("custom-name")

        with pytest.raises(
            BrandLogoMissingError,
            match="brand.logo.images\\['custom-name'\\] is required",
        ):
            brand_single_logo.use_logo("custom-name", required=True)


class TestUseLogoFromImages:
    """Test use_logo() with images dictionary"""

    @pytest.fixture
    def brand_with_images(self):
        """Brand with images dictionary"""
        return Brand.from_yaml_str("""
        logo:
          images:
            custom-logo: logo.png
            another-logo:
              path: another.png
              alt: Another Logo
          small: custom-logo
        """)

    def test_use_logo_from_images_by_name(self, brand_with_images):
        """Test access by image name"""
        logo = brand_with_images.use_logo("custom-logo")
        assert isinstance(logo, BrandLogoResource)
        assert str(logo.path) == "logo.png"
        assert logo.alt is None

        logo2 = brand_with_images.use_logo("another-logo")
        assert isinstance(logo2, BrandLogoResource)
        assert str(logo2.path) == "another.png"
        assert logo2.alt == "Another Logo"

    def test_use_logo_from_images_by_size(self, brand_with_images):
        """Test access by size"""
        small_logo = brand_with_images.use_logo("small")
        assert isinstance(small_logo, BrandLogoResource)
        assert str(small_logo.path) == "logo.png"

    def test_use_logo_from_images_nonexistent(self, brand_with_images):
        """Test accessing non-existent image"""
        assert brand_with_images.use_logo("nonexistent", required=False) is None

        with pytest.raises(
            BrandLogoMissingError,
            match="brand.logo.images\\['nonexistent'\\] is required",
        ):
            brand_with_images.use_logo("nonexistent")

        with pytest.raises(
            BrandLogoMissingError,
            match="brand.logo.images\\['nonexistent'\\] is required",
        ):
            brand_with_images.use_logo("nonexistent", required=True)


class TestUseLogoSmallestLargest:
    """Test smallest/largest convenience options"""

    @pytest.fixture
    def brand_partial_sizes(self):
        """Brand with only small and large sizes"""
        return Brand.from_yaml_str("""
        logo:
          small: small.png
          large: large.png
        """)

    @pytest.fixture
    def brand_all_sizes(self):
        """Brand with all three sizes"""
        return Brand.from_yaml_str("""
        logo:
          small: small.png
          medium: medium.png
          large: large.png
        """)

    @pytest.fixture
    def brand_with_special_names(self):
        """Brand with 'smallest' and 'largest' as named images"""
        return Brand.from_yaml_str("""
        logo:
          images:
            smallest: special-tiny.png
            largest: special-huge.png
            custom: custom-logo.png
          small: regular-small.png
          large: regular-large.png
        """)

    @pytest.fixture
    def brand_only_images(self):
        """Brand with only images, no standard sizes"""
        return Brand.from_yaml_str("""
        logo:
          images:
            custom: custom-logo.png
        """)

    @pytest.fixture
    def brand_images_with_sizes(self):
        """Brand with images and standard sizes"""
        return Brand.from_yaml_str("""
        logo:
          images:
            custom: custom-logo.png
          small: small.png
          medium: medium.png
          large: large.png
        """)

    def test_use_logo_smallest_largest_basic(self, brand_partial_sizes):
        """Test smallest/largest with partial sizes"""
        smallest = brand_partial_sizes.use_logo("smallest")
        assert isinstance(smallest, BrandLogoResource)
        assert str(smallest.path) == "small.png"

        largest = brand_partial_sizes.use_logo("largest")
        assert isinstance(largest, BrandLogoResource)
        assert str(largest.path) == "large.png"

    def test_use_logo_smallest_largest_all_sizes(self, brand_all_sizes):
        """Test smallest/largest with all sizes"""
        smallest_full = brand_all_sizes.use_logo("smallest")
        assert isinstance(smallest_full, BrandLogoResource)
        assert str(smallest_full.path) == "small.png"

        largest_full = brand_all_sizes.use_logo("largest")
        assert isinstance(largest_full, BrandLogoResource)
        assert str(largest_full.path) == "large.png"

    def test_use_logo_smallest_largest_with_images(
        self, brand_with_special_names
    ):
        """Test smallest/largest when names exist in images dictionary"""
        # When "smallest" exists in images, it should be used directly
        smallest = brand_with_special_names.use_logo("smallest")
        assert isinstance(smallest, BrandLogoResource)
        assert str(smallest.path) == "special-tiny.png"

        # When "largest" exists in images, it should be used directly
        largest = brand_with_special_names.use_logo("largest")
        assert isinstance(largest, BrandLogoResource)
        assert str(largest.path) == "special-huge.png"

        # Other custom image names should also work
        custom = brand_with_special_names.use_logo("custom")
        assert isinstance(custom, BrandLogoResource)
        assert str(custom.path) == "custom-logo.png"

    def test_use_logo_smallest_largest_no_sizes_available(
        self, brand_only_images
    ):
        """Test smallest/largest when no standard sizes are available"""
        # Should return None when no standard sizes are available
        smallest = brand_only_images.use_logo("smallest")
        assert smallest is None

        largest = brand_only_images.use_logo("largest")
        assert largest is None

        # With required=True should raise error
        with pytest.raises(
            BrandLogoMissingError,
            match="A 'small', 'medium' or 'large' logo is required",
        ):
            brand_only_images.use_logo("smallest", required=True)

        with pytest.raises(
            BrandLogoMissingError,
            match="A 'small', 'medium' or 'large' logo is required",
        ):
            brand_only_images.use_logo("largest", required=True)

        # Custom images should still work
        custom = brand_only_images.use_logo("custom")
        assert isinstance(custom, BrandLogoResource)
        assert str(custom.path) == "custom-logo.png"

    def test_use_logo_smallest_largest_fallback_to_sizes(
        self, brand_images_with_sizes
    ):
        """Test smallest/largest fallback behavior when images don't contain them"""
        # Should fall back to actual size-based selection
        smallest = brand_images_with_sizes.use_logo("smallest")
        assert isinstance(smallest, BrandLogoResource)
        assert str(smallest.path) == "small.png"

        largest = brand_images_with_sizes.use_logo("largest")
        assert isinstance(largest, BrandLogoResource)
        assert str(largest.path) == "large.png"

    def test_use_logo_smallest_largest_partial_fallback(self):
        """Test smallest/largest with partial sizes"""
        brand_partial = Brand.from_yaml_str("""
        logo:
          medium: medium.png
          large: large.png
        """)

        smallest_partial = brand_partial.use_logo("smallest")
        assert isinstance(smallest_partial, BrandLogoResource)
        assert str(smallest_partial.path) == "medium.png"

        largest_partial = brand_partial.use_logo("largest")
        assert isinstance(largest_partial, BrandLogoResource)
        assert str(largest_partial.path) == "large.png"


class TestUseLogoVariants:
    """Test variant selection with use_logo()"""

    @pytest.fixture
    def brand_mixed_variants(self):
        """Brand with mixed single and light/dark logos"""
        return Brand.from_yaml_str("""
        logo:
          small: small.png
          medium:
            light: medium-light.png
            dark: medium-dark.png
        """)

    @pytest.fixture
    def brand_partial_variants(self):
        """Brand with partial light/dark definitions"""
        return Brand.from_yaml_str("""
        logo:
          small:
            light: small-light.png
          medium:
            dark: medium-dark.png
        """)

    def test_use_logo_variant_auto_single(self, brand_mixed_variants):
        """Test variant='auto' with single logo resources"""
        # Auto with single resource returns the resource
        small = brand_mixed_variants.use_logo("small", variant="auto")
        assert isinstance(small, BrandLogoResource)
        assert str(small.path) == "small.png"

        # Auto with light/dark returns the light/dark container
        medium = brand_mixed_variants.use_logo("medium", variant="auto")
        assert isinstance(medium, BrandLogoResourceLightDark)
        assert isinstance(medium.light, BrandLogoResource)
        assert isinstance(medium.dark, BrandLogoResource)
        assert str(medium.light.path) == "medium-light.png"
        assert str(medium.dark.path) == "medium-dark.png"

    def test_use_logo_variant_auto_partial(self, brand_partial_variants):
        """Test variant='auto' with partial light/dark"""
        # Auto with only light returns light
        small = brand_partial_variants.use_logo("small", variant="auto")
        assert isinstance(small, BrandLogoResource)
        assert str(small.path) == "small-light.png"

        # Auto with only dark returns dark
        medium = brand_partial_variants.use_logo("medium", variant="auto")
        assert isinstance(medium, BrandLogoResource)
        assert str(medium.path) == "medium-dark.png"

    def test_use_logo_variant_specific(self, brand_mixed_variants):
        """Test specific variant selection"""
        # Light variant from light/dark
        medium_light = brand_mixed_variants.use_logo("medium", variant="light")
        assert isinstance(medium_light, BrandLogoResource)
        assert str(medium_light.path) == "medium-light.png"

        # Dark variant from light/dark
        medium_dark = brand_mixed_variants.use_logo("medium", variant="dark")
        assert isinstance(medium_dark, BrandLogoResource)
        assert str(medium_dark.path) == "medium-dark.png"

        # Light variant with fallback to single
        small_light = brand_mixed_variants.use_logo("small", variant="light")
        assert isinstance(small_light, BrandLogoResource)
        assert str(small_light.path) == "small.png"

        # Light variant without fallback
        assert (
            brand_mixed_variants.use_logo(
                "small", variant="light", allow_fallback=False
            )
            is None
        )

    def test_use_logo_variant_light_dark(self, brand_mixed_variants):
        """Test variant=['light', 'dark'] behavior"""
        # Light/dark from existing light/dark
        medium_both = brand_mixed_variants.use_logo(
            "medium", variant="light-dark"
        )
        assert isinstance(medium_both, BrandLogoResourceLightDark)
        assert medium_both.light is not None
        assert medium_both.dark is not None
        assert str(medium_both.light.path) == "medium-light.png"
        assert str(medium_both.dark.path) == "medium-dark.png"

        # Light/dark with fallback promotion
        small_both = brand_mixed_variants.use_logo(
            "small", variant="light-dark"
        )
        assert isinstance(small_both, BrandLogoResourceLightDark)
        assert small_both.light is not None
        assert small_both.dark is not None
        assert str(small_both.light.path) == "small.png"
        assert str(small_both.dark.path) == "small.png"

        # Light/dark without fallback
        assert (
            brand_mixed_variants.use_logo(
                "small", variant="light-dark", allow_fallback=False
            )
            is None
        )


class TestUseLogoErrors:
    """Test error conditions for use_logo()"""

    @pytest.fixture
    def brand_partial_light_dark(self):
        """Brand with partial light/dark logo"""
        return Brand.from_yaml_str("""
        logo:
          small: small.png
          medium:
            light: medium-light.png
        """)

    def test_use_logo_invalid_variant(self, brand_partial_light_dark):
        """Test invalid variant values"""
        with pytest.raises(ValueError, match="variant must be"):
            brand_partial_light_dark.use_logo("small", variant="invalid")  # type: ignore

        with pytest.raises(ValueError, match="variant must be"):
            brand_partial_light_dark.use_logo("small", variant=["light"])  # type: ignore

    def test_use_logo_missing_variant_without_fallback(
        self, brand_partial_light_dark
    ):
        """Test missing variant without fallback"""
        with pytest.raises(
            BrandLogoMissingError, match="brand.logo.medium.dark is required"
        ):
            brand_partial_light_dark.use_logo(
                "medium", variant="dark", allow_fallback=False, required=True
            )

    def test_use_logo_missing_light_dark_without_fallback(
        self, brand_partial_light_dark
    ):
        """Test missing light/dark variants without fallback"""
        with pytest.raises(
            BrandLogoMissingError,
            match="brand.logo.small with light/dark variants",
        ):
            brand_partial_light_dark.use_logo(
                "small",
                variant="light-dark",
                allow_fallback=False,
                required=True,
            )


class TestUseLogoAttrsAndFormatting:
    """Test attribute attachment and formatting methods"""

    @pytest.fixture
    def brand_with_attrs(self):
        """Brand with existing class attribute"""
        return Brand.from_yaml_str("""
        logo:
          small:
            path: small.png
            attrs:
              class: existing-class
        """)

    @pytest.fixture
    def brand_for_formatting(self):
        """Brand for testing formatting methods"""
        return Brand.from_yaml_str("""
        logo:
          small: small.png
          medium:
            light: medium-light.png
            dark: medium-dark.png
        """)

    def test_use_logo_attrs(self, brand_with_attrs):
        """Test attribute attachment"""
        # Basic attrs
        logo = brand_with_attrs.use_logo("small", width="100", height="50")
        assert isinstance(logo, BrandLogoResource)
        assert logo.attrs is not None
        assert logo.attrs["class"] == "existing-class"
        assert logo.attrs["width"] == "100"
        assert logo.attrs["height"] == "50"

        # Attrs are merged, not replaced
        logo2 = brand_with_attrs.use_logo("small", class_="new-class")
        assert isinstance(logo2, BrandLogoResource)
        assert logo2.attrs is not None
        assert logo2.attrs["class"] == "existing-class new-class"

    def test_use_logo_formatting_methods(self, brand_for_formatting):
        """Test formatting methods on returned logo resources"""
        # Single resource formatting
        logo = brand_for_formatting.use_logo("small")
        assert hasattr(logo, "to_html")
        assert hasattr(logo, "to_markdown")
        assert hasattr(logo, "to_str")
        assert hasattr(logo, "tagify")

        # Light/dark resource formatting
        logo_ld = brand_for_formatting.use_logo("medium")
        assert hasattr(logo_ld, "to_html")
        assert hasattr(logo_ld, "to_markdown")
        assert hasattr(logo_ld, "to_str")
        assert hasattr(logo_ld, "tagify")


class TestUseLogoPathResolution:
    """Test path resolution"""

    def test_use_logo_path_resolution(self):
        """Test path resolution to absolute paths"""
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


class TestUseLogoMissingSizes:
    """Test requesting missing sizes from BrandLogo"""

    @pytest.fixture
    def brand_partial_sizes(self):
        """Brand with some sizes but not all"""
        return Brand.from_yaml_str("""
        logo:
          small: small.png
          large: large.png
        """)

    @pytest.fixture
    def brand_single_resource_only(self):
        """Brand with single logo resource (no sizes)"""
        return Brand.from_yaml_str("""
        logo: single-logo.png
        """)

    def test_use_logo_missing_sizes(self, brand_partial_sizes):
        """Test requesting missing sizes"""
        # Existing sizes should work
        small = brand_partial_sizes.use_logo("small")
        large = brand_partial_sizes.use_logo("large")
        assert isinstance(small, BrandLogoResource)
        assert isinstance(large, BrandLogoResource)
        assert str(small.path) == "small.png"
        assert str(large.path) == "large.png"

        # Missing size should return None by default
        medium = brand_partial_sizes.use_logo("medium")
        assert medium is None

        # Missing size with required=True should raise error
        with pytest.raises(
            BrandLogoMissingError, match="brand.logo.medium is required"
        ):
            brand_partial_sizes.use_logo("medium", required=True)

        # Missing size with custom required message
        with pytest.raises(
            BrandLogoMissingError,
            match="brand.logo.medium is required for navbar display",
        ):
            brand_partial_sizes.use_logo(
                "medium", required="for navbar display"
            )

    def test_use_logo_single_resource_size_requests(
        self, brand_single_resource_only
    ):
        """Test requesting sizes from a single BrandLogoResource"""
        # Requesting sizes from single resource should work for convenience
        logo_small = brand_single_resource_only.use_logo("small")
        logo_medium = brand_single_resource_only.use_logo("medium")
        logo_large = brand_single_resource_only.use_logo("large")
        logo_smallest = brand_single_resource_only.use_logo("smallest")
        logo_largest = brand_single_resource_only.use_logo("largest")

        # All should return the same single logo resource
        assert isinstance(logo_small, BrandLogoResource)
        assert isinstance(logo_medium, BrandLogoResource)
        assert isinstance(logo_large, BrandLogoResource)
        assert isinstance(logo_smallest, BrandLogoResource)
        assert isinstance(logo_largest, BrandLogoResource)

        assert str(logo_small.path) == "single-logo.png"
        assert str(logo_medium.path) == "single-logo.png"
        assert str(logo_large.path) == "single-logo.png"
        assert str(logo_smallest.path) == "single-logo.png"
        assert str(logo_largest.path) == "single-logo.png"

        # Requesting a named image should fail for single resource
        assert (
            brand_single_resource_only.use_logo("custom-image", required=False)
            is None
        )

        with pytest.raises(
            BrandLogoMissingError,
            match="brand.logo.images\\['custom-image'\\] is required",
        ):
            brand_single_resource_only.use_logo("custom-image", required=True)
