from __future__ import annotations

from pydantic import ConfigDict, Field, HttpUrl, field_validator

from .base import BrandBase


class BrandMeta(BrandBase):
    """
    Brand metadata is stored in `meta`, providing place to describe the company
    or project, the brand guidelines, additional links, and more.
    """

    model_config = ConfigDict(
        extra="allow",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    name: BrandMetaName | None = Field(
        None,
        examples=["Very Big Corporation of America"],
    )

    link: BrandMetaLink | None = Field(
        None,
        examples=[
            "https://very-big-corp.com",
            '{"home": "https://very-big-corp.com"}',
        ],
    )

    @field_validator("name", mode="before")
    @classmethod
    def promote_str_name(
        cls,
        value: str | dict[str, str] | None,
    ) -> dict[str, str] | None:
        if isinstance(value, str):
            return {"full": value}
        return value

    @field_validator("link", mode="before")
    @classmethod
    def promote_str_link(
        cls,
        value: str | dict[str, str] | None,
    ) -> dict[str, str] | None:
        if isinstance(value, str):
            return {"home": value}
        return value


class BrandMetaName(BrandBase):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        revalidate_instances="always",
        validate_assignment=True,
    )

    full: str | None = Field(None, examples=["Very Big Corporation of America"])
    short: str | None = Field(None, examples=["VBC"])


class BrandMetaLink(BrandBase):
    model_config = ConfigDict(
        extra="allow",
        str_strip_whitespace=True,
        revalidate_instances="always",
        validate_assignment=True,
    )

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
