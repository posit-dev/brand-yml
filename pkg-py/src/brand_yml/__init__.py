from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from ._defs import BrandLightDark
from ._utils import (
    envvar_brand_yml_path,
    find_project_brand_yml,
    recurse_dicts_and_models,
    use_brand_yml_path,
)
from ._utils_yaml import yaml_brand as yaml
from .base import BrandBase
from .color import BrandColor
from .file import FileLocation, FileLocationLocal, FileLocationUrl
from .logo import BrandLogo, BrandLogoResource, BrandLogoResourceLightDark
from .meta import BrandMeta
from .typography import BrandTypography


class Brand(BrandBase):
    """
    Brand guidelines in a class.

    A brand instance encapsulates the color, typography and logo preferences for
    a given brand, typically found in brand guidelines created by a company's
    marketing department. `brand_yml.Brand` organizes this information in a
    common, fully-specified class instance that makes it easy to re-use for
    theming any artifact from websites to data visualizations.

    Unified brand information following the Brand YAML specification. Read brand
    metadata from a YAML file, typically named `_brand.yml`, with
    `brand_yml.Brand.from_yaml` or from a YAML string with
    `brand_yml.Brand.from_yaml_str`. Or create a full brand instance directly
    via this class.

    Attributes
    ----------
    meta
        Key identity information, name of the company, links to brand
        guidelines, etc.
    logo
        Files or links to the brand's logo at various sizes.
    color
        Named colors in the brand's color palette and semantic colors (e.g.,
        primary, secondary, success, warning).
    typography
        Font definitions, font family, weight, style, color, and line height for
        key elements (e.g., base, headings, and monospace text).
    defaults
        Additional context-specific settings beyond the basic brand colors and
        typography.
    path
        The file path of the brand configuration. This attribute is excluded
        from serialization and representation.
    """

    model_config = ConfigDict(
        extra="forbid",
        revalidate_instances="always",
        validate_assignment=True,
    )

    meta: BrandMeta | None = None
    logo: BrandLogo | BrandLogoResource | None = None
    color: BrandColor | None = None
    typography: BrandTypography | None = None
    defaults: dict[str, Any] | None = None
    path: Path | None = Field(None, exclude=True, repr=False)

    @classmethod
    def from_yaml(cls, path: str | Path | None = None):
        """
        Create a Brand instance from a Brand YAML file.

        Reads a Brand YAML file or finds and reads a `_brand.yml` file and
        returns a validated :class:`Brand` instance.

        To find a project-specific `_brand.yml` file, pass `path` the project
        directory or `__file__` (the path of the current Python script).
        [`brand_yml.Brand.from_yaml`](`brand_yml.Brand.from_yaml`) will look in
        that directory or any parent directory for a `_brand.yml`,
        `brand/_brand.yml` or `_brand/_brand.yml` file (or the same variants
        with a `.yaml` extension). Note that it starts the search in the
        directory passed in and moves upward to find the `_brand.yml` file; it
        does not search into subdirectories of the current directory.

        Parameters
        ----------
        path
            The path to the brand.yml file or a directory where `_brand.yml` is
            expected to be found. Typically, you can pass `__file__` from the
            calling script to find `_brand.yml` or `_brand.yaml` in the current
            directory or any of its parent directories. Alternatively, if no
            path is specified, the `BRAND_YML_PATH` environment variable is
            checked for the path to the brand.yml file.

        Returns
        -------
        :
            A validated `Brand` object with all fields populated according to
            the brand.yml file.

        Raises
        ------
        FileNotFoundError
            Raises a `FileNotFoundError` if no brand configuration file is found
            within the given path.
        ValueError
            Raises `ValueError` or other validation errors from
            [pydantic](https://docs.pydantic.dev/latest/) if the brand.yml file
            is invalid.

        Examples
        --------

        ```python
        from brand_yml import Brand

        brand = Brand.from_yaml(__file__)
        brand = Brand.from_yaml("path/to/_brand.yml")
        ```
        """
        if path is None:
            path = envvar_brand_yml_path()
            if path is None:
                raise ValueError(
                    "No path specified and the BRAND_YML_PATH environment "
                    "variable is not set. You likely need to pass `__file__` to "
                    "`brand_yml.Brand.from_yaml()` or set the BRAND_YML_PATH "
                    "environment variable."
                )

        path = Path(path).absolute()

        if path.is_dir() or path.suffix == ".py":
            # allows users to simply pass `__file__`
            path = find_project_brand_yml(path)

        with open(path, "r") as f:
            brand_data = yaml.load(f)

        if not isinstance(brand_data, dict):
            raise ValueError(
                f"Invalid Brand YAML file {str(path)!r}. Must be a dictionary."
            )

        brand_data["path"] = path

        return cls.model_validate(brand_data)

    @classmethod
    def from_yaml_str(cls, text: str, path: str | Path | None = None):
        """
        Create a Brand instance from a string of YAML.

        Parameters
        ----------
        text
            The text of the Brand YAML file.
        path
            The optional path on disk for supporting files like logos and fonts.

        Returns
        -------
        :
            A validated `brand_yml.Brand` object with all fields populated
            according to the Brand YAML text.

        Raises
        ------
        ValueError
            Raises `ValueError` or other validation errors from
            [pydantic](https://docs.pydantic.dev/latest/) if the Brand YAML file
            is invalid.

        Examples
        --------

        ```{python}
        from brand_yml import Brand

        brand = Brand.from_yaml_str(\"\"\"
        meta:
          name: Brand YAML
        color:
          primary: "#ff0202"
        typography:
          base: Open Sans
        \"\"\")
        ```

        ```{python}
        brand.meta
        ```

        ```{python}
        brand.color.primary
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
        Serialize the Brand object to YAML.

        Write the [`brand_yml.Brand`](`brand_yml.Brand`) instance to a string
        or to a file on disk.

        Examples
        --------

        ```{python}
        from brand_yml import Brand

        brand = Brand.from_yaml_str(\"\"\"
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
    def _resolve_typography_colors(self):
        """
        Resolve colors in `typography` using `color`.

        Resolves colors used in `brand.typography` in the `color` or
        `background-color` fields of any typography properties. These values are
        replaced when the brand instance is validated so that values are ready
        to be used by any brand consumers.
        """
        if self.typography is None:
            return self

        color_defs = self.color.to_dict() if self.color else {}
        color_names = [
            k for k in BrandColor.model_fields.keys() if k != "palette"
        ]

        for top_field in self.typography.__class__.model_fields.keys():
            typography_node = getattr(self.typography, top_field)

            if not isinstance(typography_node, BaseModel):
                continue

            for (
                typography_node_field
            ) in typography_node.__class__.model_fields.keys():
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
    def _validate_path_is_absolute(cls, value: Path | None) -> Path | None:
        """
        Ensures that the value of the `path` field is specified absolutely.

        Will also expand user directories and resolve any symlinks.
        """
        if value is None:
            return None

        value = Path(value).expanduser()

        if not value.is_absolute():
            raise ValueError(
                f"brand.path must be an absolute path, not `{value}`."
            )

        return value.resolve()

    def use_logo(
        self,
        name: str,
        variant: str | list[str] = "auto",
        *,
        required: bool | str | None = None,
        allow_fallback: bool = True,
        **kwargs: Any,
    ) -> BrandLogoResource | BrandLogoResourceLightDark | None:
        """
        Extract a logo resource from a brand.

        Returns a brand logo resource specified by name and variant from a brand
        object. The image paths in the returned object are adjusted to be
        absolute, relative to the location of the brand YAML file, if `brand`
        was read from a file, or the local working directory otherwise.

        Parameters
        ----------
        name
            The name of the logo to use. Either a size (`"small"`, `"medium"`,
            `"large"`) or an image name from `brand.logo.images`. Alternatively,
            you can also use `"smallest"` or `"largest"` to select the smallest
            or largest available logo size, respectively.
        variant
            Which variant to use, only used when `name` is one of the brand.yml
            fixed logo sizes (`"small"`, `"medium"`, or `"large"`). Can be one
            of:

            * `"auto"`: Auto-detect, returns a light/dark logo resource if both
              variants are present, otherwise it returns a single logo resource,
              either the value for `brand.logo.{name}` or the single light or
              dark variant if only one is present.
            * `"light"`: Returns only the light variant. If no light variant is
              present, but `brand.logo.{name}` is a single logo resource and
              `allow_fallback` is `True`, `use_logo()` falls back to the single
              logo resource.
            * `"dark"`: Returns only the dark variant, or, as above, falls back
              to the single logo resource if no dark variant is present and
              `allow_fallback` is `True`.
            * `["light", "dark"]`: Returns a light/dark object with both
              variants. If a single logo resource is present for
              `brand.logo.{name}` and `allow_fallback` is `True`, the single
              logo resource is promoted to a light/dark logo resource with
              identical light and dark variants.
        required
            Logical or string. If `True`, an error is thrown if the requested
            logo is not found. If a string, it is used to describe why the logo
            is required in the error message and completes the phrase `"is
            required ____"`. Defaults to `False` when `name` is one of the fixed
            sizes -- `"small"`, `"medium"`, `"large"` or `"smallest"` or
            `"largest"`. Otherwise, an error is thrown by default if the
            requested logo is not found.
        allow_fallback
            If `True` (the default), allows falling back to a
            non-variant-specific logo when a specific variant is requested. Only
            used when `name` is one of the fixed logo sizes (`"small"`,
            `"medium"`, or `"large"`).
        **kwargs
            Additional named attributes to be added to the image HTML or
            markdown when created via formatting methods.

        Returns
        -------
        :
            A `BrandLogoResource` object, a `BrandLogoResourceLightDark` object,
            or `None` if the requested logo doesn't exist and `required` is
            `False`.

        Raises
        ------
        ValueError
            If the requested logo is not found and `required` is `True` or a string.
        """
        if self.logo is None:
            if required is not False:
                reason = (
                    " " + str(required) if isinstance(required, str) else ""
                )
                raise ValueError(f"brand.logo.{name} is required{reason}.")
            return None

        # Handle required parameter
        if required is True:
            required_reason = ""
        elif required is False:
            required_reason = None
        elif isinstance(required, str):
            required_reason = " " + required.strip()
        elif required is None:
            # Default behavior: required for image names, not required for size names
            if name in {"small", "medium", "large", "smallest", "largest"}:
                required_reason = None
            else:
                required_reason = ""

        def attach_attrs(resource):
            """Add kwargs as attrs to a logo resource"""
            if kwargs and hasattr(resource, "model_copy"):
                # Handle single resource
                current_attrs = getattr(resource, "attrs", None) or {}
                new_attrs = {**current_attrs, **kwargs}
                return resource.model_copy(update={"attrs": new_attrs})
            elif (
                kwargs
                and hasattr(resource, "light")
                and hasattr(resource, "dark")
            ):
                # Handle light/dark resource - need to copy attrs to both variants
                light_attrs = (
                    getattr(resource.light, "attrs", None) or {}
                    if resource.light
                    else {}
                )
                dark_attrs = (
                    getattr(resource.dark, "attrs", None) or {}
                    if resource.dark
                    else {}
                )

                new_light = (
                    resource.light.model_copy(
                        update={"attrs": {**light_attrs, **kwargs}}
                    )
                    if resource.light
                    else None
                )
                new_dark = (
                    resource.dark.model_copy(
                        update={"attrs": {**dark_attrs, **kwargs}}
                    )
                    if resource.dark
                    else None
                )

                return BrandLogoResourceLightDark(
                    light=new_light, dark=new_dark
                )
            return resource

        # Handle "smallest" and "largest" convenience options
        if name in {"smallest", "largest"}:
            sizes = ["small", "medium", "large"]
            available = []

            # Check what sizes are available in the logo
            if isinstance(self.logo, BrandLogo):
                for size in sizes:
                    if getattr(self.logo, size, None) is not None:
                        available.append(size)

            # Also check in images
            if (
                isinstance(self.logo, BrandLogo)
                and self.logo.images
                and name in self.logo.images
            ):
                # If name exists in images, use it directly
                resource = self.logo.images[name]
                if hasattr(resource, "path") and self.path:
                    # Convert relative paths to absolute
                    if isinstance(resource.path, FileLocationLocal):
                        resource = resource.model_copy(
                            update={
                                "path": resource.path.set_root_dir(
                                    self.path.parent
                                )
                            }
                        )
                return attach_attrs(resource)

            if not available:
                if required_reason is not None:
                    raise ValueError(
                        f"No logos are available to satisfy '{name}' in brand.logo or brand.logo.images{required_reason}."
                    )
                return None

            name = available[0] if name == "smallest" else available[-1]

        # Check if name exists in images
        if (
            isinstance(self.logo, BrandLogo)
            and self.logo.images
            and name in self.logo.images
        ):
            resource = self.logo.images[name]
            if hasattr(resource, "path") and self.path:
                # Convert relative paths to absolute
                if isinstance(resource.path, FileLocationLocal):
                    resource = resource.model_copy(
                        update={
                            "path": resource.path.set_root_dir(self.path.parent)
                        }
                    )
            return attach_attrs(resource)

        # Check if name is a standard size
        if name not in {"small", "medium", "large"}:
            if required_reason is not None:
                raise ValueError(
                    f"brand.logo.images['{name}'] is required{required_reason}."
                )
            return None

        # Handle standard sizes (small, medium, large)
        if not isinstance(self.logo, BrandLogo):
            # logo is a single BrandLogoResource, not a BrandLogo with sizes
            if required_reason is not None:
                raise ValueError(
                    f"brand.logo.{name} is required{required_reason}."
                )
            return None

        size_logo = getattr(self.logo, name, None)
        if size_logo is None:
            if required_reason is not None:
                raise ValueError(
                    f"brand.logo.{name} is required{required_reason}."
                )
            return None

        # Process variant parameter
        if isinstance(variant, list):
            if set(variant) == {"light", "dark"}:
                variant = "light_dark"
            else:
                raise ValueError(
                    "variant list must be exactly ['light', 'dark']"
                )
        elif variant not in {"auto", "light", "dark"}:
            raise ValueError(
                "variant must be 'auto', 'light', 'dark', or ['light', 'dark']"
            )

        # Determine if we have a light/dark variant
        has_light_dark = isinstance(
            size_logo, (BrandLightDark, BrandLogoResourceLightDark)
        )

        # Fix up internal paths to be relative to brand yml file
        if has_light_dark:
            if (
                size_logo.light
                and hasattr(size_logo.light, "path")
                and self.path
            ):
                if isinstance(size_logo.light.path, FileLocationLocal):
                    size_logo = size_logo.model_copy(
                        update={
                            "light": size_logo.light.model_copy(
                                update={
                                    "path": size_logo.light.path.set_root_dir(
                                        self.path.parent
                                    )
                                }
                            )
                        }
                    )
            if size_logo.dark and hasattr(size_logo.dark, "path") and self.path:
                if isinstance(size_logo.dark.path, FileLocationLocal):
                    size_logo = size_logo.model_copy(
                        update={
                            "dark": size_logo.dark.model_copy(
                                update={
                                    "path": size_logo.dark.path.set_root_dir(
                                        self.path.parent
                                    )
                                }
                            )
                        }
                    )
        else:
            if hasattr(size_logo, "path") and self.path:
                if isinstance(size_logo.path, FileLocationLocal):
                    size_logo = size_logo.model_copy(
                        update={
                            "path": size_logo.path.set_root_dir(
                                self.path.parent
                            )
                        }
                    )

        # Implement variant logic based on the table from R implementation
        if variant == "auto":
            if not has_light_dark:
                # Case A.1: Return single value as-is
                return attach_attrs(size_logo)

            if size_logo.light is not None and size_logo.dark is not None:
                # Case A.2: Return light_dark if both variants exist
                return attach_attrs(size_logo)

            if size_logo.light is not None:
                # Case A.3: Return light if only light exists
                return attach_attrs(size_logo.light)

            if size_logo.dark is not None:
                # Case A.4: Return dark if only dark exists
                return attach_attrs(size_logo.dark)

        elif variant == "light_dark":
            if has_light_dark:
                # Case B.1: Return light_dark if both variants exist
                return attach_attrs(size_logo)

            if allow_fallback:
                # Case B.2: Promote single to light_dark if fallback allowed
                # At this point we know size_logo is a single BrandLogoResource
                single_resource = cast(BrandLogoResource, size_logo)
                return attach_attrs(
                    BrandLogoResourceLightDark(
                        light=single_resource, dark=single_resource
                    )
                )

            # Case B.3: No fallback allowed, error or return NULL
            if required_reason is not None:
                raise ValueError(
                    f"brand.logo.{name} requires light/dark variants{required_reason}."
                )
            return None

        else:  # variant is "light" or "dark"
            if has_light_dark:
                # Case C: return specific variant if it exists
                variant_resource = getattr(size_logo, variant, None)
                if variant_resource is not None:
                    return attach_attrs(variant_resource)
            else:
                # Case D: return single if fallback allowed
                if allow_fallback:
                    return attach_attrs(size_logo)

            # Case X: specific variant doesn't exist and can't fallback
            if required_reason is not None:
                raise ValueError(
                    f"brand.logo.{name}.{variant} is required{required_reason}."
                )
            return None

    @model_validator(mode="after")
    def _set_root_path(self):
        """
        Update the root path of local file locations.

        Updates any fields in `brand_yml.Brand` that are known local file
        locations, i.e. fields that are validated into
        `brand_yml.file.FileLocationLocal` instances, to record the root
        directory. These file paths should be specified (and serialized) as
        relative paths in `_brand.yml`, but any brand consumer will need to be
        able to resolve the file locations to their absolute paths via
        `brand_yml.file.FileLocationLocal.absolute()`.
        """
        path = self.path
        if path is not None:
            recurse_dicts_and_models(
                self,
                pred=lambda value: isinstance(value, FileLocationLocal),
                modify=lambda value: value.set_root_dir(path.parent),
            )

        return self

    @field_validator("logo", mode="before")
    @classmethod
    def _promote_logo_scalar_to_resource(cls, value: Any):
        """
        Take a single path value passed to `brand.logo` and promote it into a
        [`brand_yml.BrandLogoResource`](`brand_yml.BrandLogoResource`).
        """
        if isinstance(value, (str, Path, FileLocation)):
            return {"path": value}
        return value


__all__ = [
    "Brand",
    "BrandMeta",
    "BrandLogo",
    "BrandColor",
    "BrandTypography",
    "BrandLightDark",
    "BrandLogoResource",
    "BrandLogoResourceLightDark",
    "FileLocation",
    "FileLocationLocal",
    "FileLocationUrl",
    "find_project_brand_yml",
    "use_brand_yml_path",
]
