from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, overload

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from ._utils import find_project_brand_yaml, recurse_dicts_and_models
from ._utils_yaml import yaml_brand as yaml
from .color import BrandColor
from .file import FileLocationLocal
from .logo import BrandLogo
from .meta import BrandMeta
from .typography import BrandTypography


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

    @classmethod
    def from_yaml_str(cls, text: str, path: str | Path | None = None):
        """
        Create a Brand instance from a YAML string

        Parameters
        ----------
        text
            The text of the brand YAML file.
        path
            The optional path on disk for supporting files like logos and fonts.

        Returns
        -------
        :
            A validated :class:`Brand` object with all fields populated according to
            the brand YAML text.

        Raises
        ------
        :
            Raises `ValueError` or other validation errors from
            [pydantic](https://docs.pydantic.dev/latest/) if the brand YAML file
            is invalid.

        Examples
        --------

        ```python
        from brand_yaml import Brand

        brand = Brand.from_yaml_str(\"\"\"
        meta:
          name: Brand YAML
        color:
          primary: "#ff0202"
        typography:
          base: Open Sans
        \"\"\")
        ```
        """
        data = yaml.load(text)

        if path is not None:
            data["path"] = Path(path).absolute()

        return cls.model_validate(data)

    def model_dump_yaml(
        self,
        stream: Any = None,
        *,
        transform: Any = None,
    ) -> Any:
        """
        Serialize the Brand object to a YAML file on disk or to a string.

        Examples
        --------

        ```{python}
        from brand_yaml import Brand

        brand = Brand.from_yaml(\"\"\"
        meta:
          name: Brand YAML
        color:
          palette:
            orange: "#ff9a02"
          primary: orange
        typography:
          headings: Raleway
        \"\"\")
        ```

        ::: python-code-preview
        ```{python}
        print(brand.model_dump_yaml())
        ```
        :::

        Parameters
        ----------
        stream
            Passed to `stream` parameter of
            [`ruamel.yaml.YAML.dump`](`ruamel.yaml.YAML.dump`).

        transform
            Passed to `transform` parameter of
            [`ruamel.yaml.YAML.dump`](`ruamel.yaml.YAML.dump`).

        Returns
        -------
        :
            A string with the YAML representation of the `brand` if `stream` is
            `None`. Otherwise, the YAML representation is written to `stream`,
            typically a file.

            Note that the output YAML may not be 100% identical to the input
            `_brand.yml`. The output will contain the fully validated Brand
            instance where default or computed values may be included as well as
            any values resolved during validation, such as colors.
        """

        return yaml.dump(self, stream=stream, transform=transform)

    @model_validator(mode="after")
    def resolve_typography_colors(self):
        if self.typography is None:
            return self

        color_defs = self.color._color_defs(resolved=True) if self.color else {}
        color_names = [
            k for k in BrandColor.model_fields.keys() if k != "palette"
        ]

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

                is_defined = value in color_defs
                is_theme_color = value in color_names

                if not is_defined:
                    if is_theme_color:
                        raise ValueError(
                            f"`typography.{top_field}.{typography_node_field}` "
                            f"referred to `color.{value}` which is not defined."
                        )
                    else:
                        continue

                setattr(
                    typography_node,
                    typography_node_field,
                    color_defs[value],
                )

        return self

    @field_validator("path", mode="after")
    @classmethod
    def validate_path_is_absolute(cls, value: Path | None) -> Path | None:
        if value is None:
            return None

        value = Path(value).expanduser()

        if not value.is_absolute():
            raise ValueError(
                f"brand.path must be an absolute path, not `{value}`."
            )

        return value.resolve()

    @model_validator(mode="after")
    def set_root_path(self):
        path = self.path
        if path is not None:
            recurse_dicts_and_models(
                self,
                pred=lambda value: isinstance(value, FileLocationLocal),
                modify=lambda value: value.set_root_dir(path.parent),
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
