import pytest
from brand_yaml import read_brand_yaml
from brand_yaml._brand_meta import BrandMeta
from pydantic import HttpUrl
from utils import path_examples


def test_brand_meta():
    meta = BrandMeta(
        name={"full": "Very Big Corporation of America ", "short": " VBC "},
        link={"home": "https://very-big-corp.com"},
    )
    assert meta.name.full == "Very Big Corporation of America"
    assert meta.name.short == "VBC"
    assert meta.link.home == HttpUrl("https://very-big-corp.com/")


def test_brand_meta_bad_url():
    with pytest.raises(ValueError):
        BrandMeta(
            name={"full": "Very Big Corporation of America ", "short": " VBC "},
            link={"home": "not-a-url"},
        )


def test_brand_meta_yaml_full():
    brand = read_brand_yaml(path_examples("brand-meta-full.yml"))

    assert brand.meta.name.full == "Very Big Corporation of America"
    assert brand.meta.name.short == "VBC"
    assert brand.meta.link.home == HttpUrl("https://very-big-corp.com")
    assert brand.meta.link.mastodon == HttpUrl(
        "https://mastodon.social/@VeryBigCorpOfficial"
    )
    assert brand.meta.link.github == HttpUrl("https://github.com/Very-Big-Corp")
    assert brand.meta.link.linkedin == HttpUrl(
        "https://linkedin.com/company/very-big-corp"
    )
    assert brand.meta.link.twitter == HttpUrl("https://twitter.com/VeryBigCorp")
    assert brand.meta.link.facebook == HttpUrl("https://facebook.com/Very-Big-Corp")

def test_brand_meta_yaml_small():
    brand = read_brand_yaml(path_examples("brand-meta-small.yml"))

    assert brand.meta.name == "Very Big Corp. of America"
    assert brand.meta.link == HttpUrl("https://very-big-corp.com")
