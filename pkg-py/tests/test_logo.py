from __future__ import annotations

from pathlib import Path

import pytest
from brand_yml import Brand
from brand_yml._defs import BrandLightDark
from brand_yml.file import FileLocation, FileLocationLocal
from brand_yml.logo import BrandLogo, BrandLogoResource
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
