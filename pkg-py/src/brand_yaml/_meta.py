from __future__ import annotations

from pydantic import BaseModel, ConfigDict, HttpUrl, Field


class BrandMeta(BaseModel):
    """
    Brand metadata is stored in `meta`, providing place to describe the company
    or project, the brand guidelines, additional links, and more.
    """

    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)

    name: str | BrandMetaName = Field(
        None, examples=["Very Big Corporation of America"]
    )
    link: HttpUrl | BrandLink = Field(
        None,
        examples=[
            "https://very-big-corp.com",
            '{"home": "https://very-big-corp.com"}',
        ],
    )


class BrandMetaName(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    full: str = Field(None, examples=["Very Big Corporation of America"])
    short: str = Field(None, examples=["VBC"])


class BrandLink(BaseModel):
    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)

    home: HttpUrl = Field(
        None,
        examples=["https://very-big-corp.com"],
    )
    mastodon: HttpUrl = Field(
        None,
        examples=["https://mastodon.social/@VeryBigCorpOfficial"],
    )
    github: HttpUrl = Field(
        None,
        examples=["https://github.com/Very-Big-Corp"],
    )
    linkedin: HttpUrl = Field(
        None,
        examples=["https://linkedin.com/company/very-big-corp"],
    )
    twitter: HttpUrl = Field(
        None,
        examples=["https://twitter.com/VeryBigCorp"],
    )
    facebook: HttpUrl = Field(
        None,
        examples=["https://facebook.com/Very-Big-Corp"],
    )
