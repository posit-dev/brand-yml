from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, overload

from pydantic import BaseModel, ConfigDict, Field, model_validator
from ruamel.yaml import YAML

from ._path import FileLocation
from ._utils import find_project_brand_yaml, recurse_dicts_and_models
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
    path: Path | None = Field(None, exclude=True, repr=False)

    @classmethod
    def from_yaml(cls, path: str | Path):
        """
        Read a brand YAML file

        Reads a brand YAML file or finds and reads a `_brand.yml` file and returns
        a validated :class:`Brand` object.

        Parameters
        ----------
        path
            The path to the brand YAML file or a directory where `_brand.yml` is
            expected to be found. Typically, you can pass `__file__` from the
            calling script to find `_brand.yml` in the current directory or any of
            its parent directories.

        Returns
        -------
        :
            A validated :class:`Brand` object with all fields populated according to
            the brand YAML file.

        Raises
        ------
        :
            Raises a `FileNotFoundError` if no brand configuration file is found
            within the given path. Raises `ValueError` or other validation errors
            from [pydantic](https://docs.pydantic.dev/latest/) if the brand YAML
            file is invalid.

        Examples
        --------

        ```python
        from brand_yaml import Brand

        brand = Brand.from_yaml(__file__)
        brand = Brand.from_yaml("path/to/_brand.yml")
        ```
        """
        return cls.model_validate(read_brand_yaml(path, as_data=True))

    @model_validator(mode="after")
    def resolve_typography_colors(self):
        if self.typography is None or self.color is None:
            return self

        color_defs = self.color._color_defs(resolved=True)

        for top_field in self.typography.model_fields.keys():
            typography_node = getattr(self.typography, top_field)

            if not isinstance(typography_node, BaseModel):
                continue

            for typography_node_field in typography_node.model_fields.keys():
                if typography_node_field not in ("color", "background_color"):
                    continue

                value = getattr(typography_node, typography_node_field)
                if value is None or not isinstance(value, str):
                    continue

                if value not in color_defs:
                    continue

                setattr(
                    typography_node,
                    typography_node_field,
                    color_defs[value],
                )

        return self

    @model_validator(mode="after")
    def resolve_paths(self):
        path = self.path
        if path is not None:
            recurse_dicts_and_models(
                self,
                pred=lambda value: isinstance(value, FileLocation),
                modify=lambda value: value.set_root_dir(
                    path.parent,
                    validate_path=True,
                ),
            )
        return self


@overload
def read_brand_yaml(
    path: str | Path, as_data: Literal[False] = False
) -> Brand: ...


@overload
def read_brand_yaml(path: str | Path, as_data: Literal[True]) -> dict: ...


def read_brand_yaml(path: str | Path, as_data: bool = False) -> Brand | dict:
    """
    Read a brand YAML file

    Reads a brand YAML file or finds and reads a `_brand.yml` file and returns
    a validated :class:`Brand` object.

    Parameters
    ----------
    path
        The path to the brand YAML file or a directory where `_brand.yml` is
        expected to be found. Typically, you can pass `__file__` from the
        calling script to find `_brand.yml` in the current directory or any of
        its parent directories.

    as_data
        When `True`, returns the raw brand data as a dictionary parsed from the
        YAML file. When `False`, returns a validated :class:`Brand` object.

    Returns
    -------
    :
        A validated :class:`Brand` object with all fields populated according to
        the brand YAML file (`as_data=False`, default) or the raw brand data
        as a dictionary (`as_data=True`).

    Raises
    ------
    :
        Raises a `FileNotFoundError` if no brand configuration file is found
        within the given path. Raises `ValueError` or other validation errors
        from [pydantic](https://docs.pydantic.dev/latest/) if the brand YAML
        file is invalid.

    Examples
    --------

    ```python
    from brand_yaml import read_brand_yaml

    brand = read_brand_yaml(__file__)
    brand = read_brand_yaml("path/to/_brand.yml")
    ```
    """

    path = Path(path).absolute()

    if path.is_dir():
        path = find_project_brand_yaml(path)
    elif path.suffix == ".py":
        # allows users to simply pass `__file__`
        path = find_project_brand_yaml(path.parent)

    with open(path, "r") as f:
        brand_data = yaml.load(f)

    if not isinstance(brand_data, dict):
        raise ValueError(
            f"Invalid brand YAML file {str(path)!r}. Must be a dictionary."
        )

    brand_data["path"] = path

    if as_data:
        return brand_data

    return Brand.model_validate(brand_data)


__all__ = [
    "Brand",
    "read_brand_yaml",
]
