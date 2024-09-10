from __future__ import annotations

import pytest
from utils import path_examples

from brand_yaml import read_brand_yaml
from brand_yaml.meta import BrandMeta, BrandMetaLink


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
    assert str(meta_empty_name.link) == "https://example.com/"

    meta_empty_link = BrandMeta(
        name="Very Big Corporation of America",
        link=None,
    )
    assert meta_empty_link.name == "Very Big Corporation of America"
    assert meta_empty_link.link is None


def test_brand_meta_bad_url():
    with pytest.raises(ValueError):
        BrandMeta(
            name={"full": "Very Big Corporation of America ", "short": " VBC "},  # type: ignore
            link={"home": "not-a-url"},  # type: ignore
        )


def test_brand_meta_yaml_full():
    brand = read_brand_yaml(path_examples("brand-meta-full.yml"))

    assert brand.meta is not None
    assert brand.meta.name is not None
    assert not isinstance(brand.meta.name, str)
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


def test_brand_meta_yaml_small():
    brand = read_brand_yaml(path_examples("brand-meta-small.yml"))

    assert brand.meta is not None
    assert brand.meta.name == "Very Big Corp. of America"
    assert str(brand.meta.link) == "https://very-big-corp.com/"