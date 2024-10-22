from __future__ import annotations

import pytest
from brand_yml import Brand
from brand_yml.meta import BrandMeta, BrandMetaLink, BrandMetaName
from syrupy.extensions.json import JSONSnapshotExtension
from utils import path_examples, pydantic_data_from_json


@pytest.fixture
def snapshot_json(snapshot):
    return snapshot.use_extension(JSONSnapshotExtension)


def test_brand_meta():
    meta = BrandMeta.model_validate(
        {
            "name": {
                "full": "Very Big Corporation of America ",
                "short": " VBC ",
            },
            "link": {"home": "https://very-big-corp.com"},
        }
    )

    assert meta.name is not None
    assert not isinstance(meta.name, str)
    assert meta.name.full == "Very Big Corporation of America"
    assert meta.name.short == "VBC"

    assert meta.link is not None
    assert isinstance(meta.link, BrandMetaLink)
    assert str(meta.link.home) == "https://very-big-corp.com/"


def test_brand_meta_empty():
    meta = BrandMeta(name=None, link=None)
    assert meta.name is None
    assert meta.link is None

    meta_empty_name = BrandMeta(name=None, link="https://example.com")  # type: ignore
    assert meta_empty_name.name is None
    assert isinstance(meta_empty_name.link, BrandMetaLink)
    assert str(meta_empty_name.link.home) == "https://example.com/"

    meta_empty_link = BrandMeta.model_validate(
        {
            "name": "Very Big Corporation of America",
            "link": None,
        }
    )
    assert isinstance(meta_empty_link.name, BrandMetaName)
    assert meta_empty_link.name.full == "Very Big Corporation of America"
    assert meta_empty_link.link is None


def test_brand_meta_bad_url():
    with pytest.raises(ValueError):
        BrandMeta(
            name={"full": "Very Big Corporation of America ", "short": " VBC "},  # type: ignore
            link={"home": "not-a-url"},  # type: ignore
        )


def test_brand_meta_ex_full(snapshot_json):
    brand = Brand.from_yaml(path_examples("brand-meta-full.yml"))

    assert brand.meta is not None
    assert brand.meta.name is not None
    assert isinstance(brand.meta.name, BrandMetaName)
    assert brand.meta.name.full == "Very Big Corporation of America"
    assert brand.meta.name.short == "VBC"

    assert brand.meta.link is not None
    assert isinstance(brand.meta.link, BrandMetaLink)
    assert str(brand.meta.link.home) == "https://very-big-corp.com/"
    assert (
        str(brand.meta.link.mastodon)
        == "https://mastodon.social/@VeryBigCorpOfficial"
    )
    assert str(brand.meta.link.github) == "https://github.com/Very-Big-Corp"
    assert (
        str(brand.meta.link.linkedin)
        == "https://linkedin.com/company/very-big-corp"
    )
    assert str(brand.meta.link.twitter) == "https://twitter.com/VeryBigCorp"
    assert str(brand.meta.link.facebook) == "https://facebook.com/Very-Big-Corp"

    assert snapshot_json == pydantic_data_from_json(brand)


def test_brand_meta_ex_small(snapshot_json):
    brand = Brand.from_yaml(path_examples("brand-meta-small.yml"))

    assert brand.meta is not None
    assert isinstance(brand.meta.name, BrandMetaName)
    assert brand.meta.name.full == "Very Big Corp. of America"
    assert isinstance(brand.meta.link, BrandMetaLink)
    assert str(brand.meta.link.home) == "https://very-big-corp.com/"

    assert snapshot_json == pydantic_data_from_json(brand)
