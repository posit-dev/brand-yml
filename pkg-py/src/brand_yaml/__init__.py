from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from ruamel.yaml import YAML

from .color import BrandColor
from .logo import BrandLogo
from .meta import BrandMeta
from .typography import BrandTypography

yaml = YAML()


class Brand(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        revalidate_instances="always",
        validate_assignment=True,
    )

    meta: BrandMeta | None = Field(None)
    logo: str | BrandLogo | None = Field(None)
    color: BrandColor | None = Field(None)
    typography: BrandTypography | None = Field(None)
    defaults: dict[str, Any] | None = Field(None)


def read_brand_yaml(path: str | Path) -> Brand:
    path = Path(path)

    with open(path, "r") as f:
        brand_data = yaml.load(f)

    return Brand.model_validate(brand_data)


__all__ = [
    "Brand",
    "read_brand_yaml",
]
