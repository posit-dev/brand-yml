from __future__ import annotations

from pathlib import Path

import pytest
from brand_yaml import read_brand_yaml
from brand_yaml._defs import BrandLightDark
from brand_yaml.file import FileLocation, FileLocationLocal
from brand_yaml.logo import BrandLogo
from syrupy.extensions.json import JSONSnapshotExtension
from utils import path_examples, pydantic_data_from_json


@pytest.fixture
def snapshot_json(snapshot):
    return snapshot.use_extension(JSONSnapshotExtension)


def test_brand_logo_single():
    brand = read_brand_yaml(path_examples("brand-logo-single.yml"))

    assert brand.logo == "posit.png"


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
    brand = read_brand_yaml(path_examples("brand-logo-simple.yml"))

    assert isinstance(brand.logo, BrandLogo)

    assert isinstance(brand.logo.small, FileLocation)
    assert str(brand.logo.small) == "logos/pandas/pandas_mark.svg"

    assert isinstance(brand.logo.medium, FileLocation)
    assert str(brand.logo.medium) == "logos/pandas/pandas_secondary.svg"

    assert isinstance(brand.logo.large, FileLocation)
    assert str(brand.logo.large) == "logos/pandas/pandas.svg"

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_logo_ex_light_dark(snapshot_json):
    brand = read_brand_yaml(path_examples("brand-logo-light-dark.yml"))

    assert isinstance(brand.logo, BrandLogo)
    assert isinstance(brand.logo.small, FileLocationLocal)
    assert str(brand.logo.small) == "logos/pandas/pandas_mark.svg"

    assert isinstance(brand.logo.medium, BrandLightDark)
    assert isinstance(brand.logo.medium.light, FileLocationLocal)
    assert str(brand.logo.medium.light) == "logos/pandas/pandas_secondary.svg"
    assert isinstance(brand.logo.medium.dark, FileLocationLocal)
    assert (
        str(brand.logo.medium.dark) == "logos/pandas/pandas_secondary_white.svg"
    )

    assert isinstance(brand.logo.large, FileLocationLocal)
    assert str(brand.logo.large) == "logos/pandas/pandas.svg"

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_logo_ex_full(snapshot_json):
    brand = read_brand_yaml(path_examples("brand-logo-full.yml"))

    assert isinstance(brand.logo, BrandLogo)
    assert isinstance(brand.logo.images, dict)
    assert isinstance(brand.logo.small, FileLocationLocal)
    assert brand.logo.small == brand.logo.images["mark"]

    assert isinstance(brand.logo.medium, BrandLightDark)
    assert isinstance(brand.logo.medium.light, FileLocationLocal)
    assert brand.logo.medium.light.root == Path(
        "logos/pandas/pandas_secondary.svg"
    )
    assert brand.logo.medium.dark == brand.logo.images["secondary-white"]

    assert isinstance(brand.logo.large, FileLocationLocal)
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
