"""
Brand Metadata

Brand metadata is stored in `meta`, providing place to describe the company
or project, the brand guidelines, additional links, and more.
"""

from __future__ import annotations

from pydantic import ConfigDict, Field, HttpUrl, field_validator

from ._utils_docs import add_example_yaml
from .base import BrandBase


@add_example_yaml(
    {"path": "brand-meta-small.yml", "name": "Minimal"},
    {"path": "brand-meta-full.yml", "name": "Full"},
)
class BrandMeta(BrandBase):
    """
    Brand Metadata

    Brand metadata is stored in `meta`, providing place to describe the company
    or project, the brand guidelines, additional links, and more.

    Attributes
    ----------
    name
        The name of the brand. In the YAML, this may be a dictionary with the
        `full` and `short` forms of the brand name.

        ```yaml
        meta:
          name:
            full: Very Big Corporation of America
            short: VBCA
        ```

        or a single value as shorthand for `meta.name.full`.

        ```yaml
        meta:
          name: Very Big Corporation of America
        ```

    link
        Links to additional resources related to the brand, such as its
        homepage, social media accounts, etc. Like `name`, this can be a single
        value or a dictionary with additional keys. If a single value is
        provided, it is promoted to the `home` key of
        `brand_yaml.meta.BrandMetaLink`.

        These two constructions are equivalent:

        ```yaml
        meta:
          link: https://www.very-big-corp.com/
        ```

        ```yaml
        meta:
          link:
            home: https://www.very-big-corp.com/
        ```
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
    """Full name of the company or brand."""
    short: str | None = Field(None, examples=["VBC"])
    """Short name of the company or brand, for use in space-constrained settings."""


class BrandMetaLink(BrandBase):
    """
    Brand Metadata Links

    Links to the brand or company online and on social media sites. Links must
    be the full URL to the social media profile. Additional fields are allowed,
    but only the attributes listed below are validated.
    """

    model_config = ConfigDict(
        extra="allow",
        str_strip_whitespace=True,
        revalidate_instances="always",
        validate_assignment=True,
    )

    # TODO: Use field validation to promote user names into the full URL.

    home: HttpUrl | None = Field(
        None,
        examples=["https://very-big-corp.com"],
    )
    """Home website link for the brand or company."""
    mastodon: HttpUrl | None = Field(
        None,
        examples=["https://mastodon.social/@VeryBigCorpOfficial"],
    )
    """Mastodon link for the brand or company."""
    github: HttpUrl | None = Field(
        None,
        examples=["https://github.com/Very-Big-Corp"],
    )
    """GitHub link for the brand or company."""
    linkedin: HttpUrl | None = Field(
        None,
        examples=["https://linkedin.com/company/very-big-corp"],
    )
    """LinkedIn link for the brand or company."""
    twitter: HttpUrl | None = Field(
        None,
        examples=["https://twitter.com/VeryBigCorp"],
    )
    """Twitter link for the brand or company."""
    facebook: HttpUrl | None = Field(
        None,
        examples=["https://facebook.com/Very-Big-Corp"],
    )
    """Facebook link for the brand or company."""
