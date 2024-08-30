from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict
from ruamel.yaml import YAML

from ._meta import BrandMeta

yaml = YAML()


class Brand(BaseModel):
    model_config = ConfigDict(extra="ignore", revalidate_instances="always")

    meta: BrandMeta = None
    # logo: str | BrandLogo = None
    # color: BrandColor = None
    # typography: BrandTypography = None
    # defaults: dict[str, Any] = None


def read_brand_yaml(path: str | Path) -> Brand:
    path = Path(path)

    with open(path, "r") as f:
        brand_data = yaml.load(f)

    return Brand.model_validate(brand_data)


__all__ = [
    "Brand",
    "read_brand_yaml",
]
