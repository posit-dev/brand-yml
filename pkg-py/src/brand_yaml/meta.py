from __future__ import annotations

from pydantic import ConfigDict, Field, HttpUrl

from ._utils import BrandBase


class BrandMeta(BrandBase):
    """
    Brand metadata is stored in `meta`, providing place to describe the company
    or project, the brand guidelines, additional links, and more.
    """

    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)

    name: str | BrandMetaName | None = Field(
        None, examples=["Very Big Corporation of America"]
    )
    link: HttpUrl | BrandMetaLink | None = Field(
        None,
        examples=[
            "https://very-big-corp.com",
            '{"home": "https://very-big-corp.com"}',
        ],
    )


class BrandMetaName(BrandBase):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    full: str | None = Field(None, examples=["Very Big Corporation of America"])
    short: str | None = Field(None, examples=["VBC"])


class BrandMetaLink(BrandBase):
    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)

    home: HttpUrl | None = Field(
        None,
        examples=["https://very-big-corp.com"],
    )
    mastodon: HttpUrl | None = Field(
        None,
        examples=["https://mastodon.social/@VeryBigCorpOfficial"],
    )
    github: HttpUrl | None = Field(
        None,
        examples=["https://github.com/Very-Big-Corp"],
    )
    linkedin: HttpUrl | None = Field(
        None,
        examples=["https://linkedin.com/company/very-big-corp"],
    )
    twitter: HttpUrl | None = Field(
        None,
        examples=["https://twitter.com/VeryBigCorp"],
    )
    facebook: HttpUrl | None = Field(
        None,
        examples=["https://facebook.com/Very-Big-Corp"],
    )
