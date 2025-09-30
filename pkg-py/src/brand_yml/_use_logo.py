from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, overload

if TYPE_CHECKING:
    from . import Brand
from ._defs import BrandLightDark
from .file import FileLocationLocal
from .logo import BrandLogo, BrandLogoResource, BrandLogoResourceLightDark


def use_logo(
    brand: Brand,
    name: str,
    variant: str | list[str] = "auto",
    *,
    required: bool | str | None = None,
    allow_fallback: bool = True,
    **kwargs: Any,
) -> BrandLogoResource | BrandLogoResourceLightDark | None:
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

    if brand.logo is None:
        if required_reason is not None:
            raise ValueError(f"brand.logo.{name} is required{required_reason}.")
        return None

    if isinstance(brand.logo, BrandLogoResource):
        if name in {"small", "medium", "large", "smallest", "largest"}:
            return logo_attach_attrs(brand.logo, kwargs)
        else:
            if required_reason is not None:
                raise ValueError(
                    f"brand.logo.images['{name}'] is required{required_reason}."
                )
            return None

    # Handle "smallest" and "largest" convenience options
    if name in {"smallest", "largest"}:
        sizes = ["small", "medium", "large"]
        available = []

        # Check what sizes are available in the logo
        if isinstance(brand.logo, BrandLogo):
            for size in sizes:
                if getattr(brand.logo, size, None) is not None:
                    available.append(size)

        # Also check in images
        if (
            isinstance(brand.logo, BrandLogo)
            and brand.logo.images
            and name in brand.logo.images
        ):
            # If name exists in images, use it directly
            resource = brand.logo.images[name]
            if hasattr(resource, "path") and brand.path:
                # Convert relative paths to absolute
                if isinstance(resource.path, FileLocationLocal):
                    resource = resource.model_copy(
                        update={
                            "path": resource.path.set_root_dir(
                                brand.path.parent
                            )
                        }
                    )
            return logo_attach_attrs(resource, kwargs)

        if not available:
            if required_reason is not None:
                raise ValueError(
                    f"No logos are available to satisfy '{name}' in brand.logo or brand.logo.images{required_reason}."
                )
            return None

        name = available[0] if name == "smallest" else available[-1]

    # Check if name exists in images
    if (
        isinstance(brand.logo, BrandLogo)
        and brand.logo.images
        and name in brand.logo.images
    ):
        resource = brand.logo.images[name]
        if hasattr(resource, "path") and brand.path:
            # Convert relative paths to absolute
            if isinstance(resource.path, FileLocationLocal):
                resource = resource.model_copy(
                    update={
                        "path": resource.path.set_root_dir(brand.path.parent)
                    }
                )
        return logo_attach_attrs(resource, kwargs)

    # Check if name is a standard size
    if name not in {"small", "medium", "large"}:
        if required_reason is not None:
            raise ValueError(
                f"brand.logo.images['{name}'] is required{required_reason}."
            )
        return None

    # Handle standard sizes (small, medium, large)
    if not isinstance(brand.logo, BrandLogo):
        # logo is a single BrandLogoResource, not a BrandLogo with sizes
        if required_reason is not None:
            raise ValueError(f"brand.logo.{name} is required{required_reason}.")
        return None

    size_logo = getattr(brand.logo, name, None)
    if size_logo is None:
        if required_reason is not None:
            raise ValueError(f"brand.logo.{name} is required{required_reason}.")
        return None

    # Process variant parameter
    if isinstance(variant, list):
        if set(variant) == {"light", "dark"}:
            variant = "light_dark"
        else:
            raise ValueError("variant list must be exactly ['light', 'dark']")
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
        if size_logo.light and hasattr(size_logo.light, "path") and brand.path:
            if isinstance(size_logo.light.path, FileLocationLocal):
                size_logo = size_logo.model_copy(
                    update={
                        "light": size_logo.light.model_copy(
                            update={
                                "path": size_logo.light.path.set_root_dir(
                                    brand.path.parent
                                )
                            }
                        )
                    }
                )
        if size_logo.dark and hasattr(size_logo.dark, "path") and brand.path:
            if isinstance(size_logo.dark.path, FileLocationLocal):
                size_logo = size_logo.model_copy(
                    update={
                        "dark": size_logo.dark.model_copy(
                            update={
                                "path": size_logo.dark.path.set_root_dir(
                                    brand.path.parent
                                )
                            }
                        )
                    }
                )
    else:
        if hasattr(size_logo, "path") and brand.path:
            if isinstance(size_logo.path, FileLocationLocal):
                size_logo = size_logo.model_copy(
                    update={
                        "path": size_logo.path.set_root_dir(brand.path.parent)
                    }
                )

    # Implement variant logic based on the table from R implementation
    if variant == "auto":
        if not has_light_dark:
            # Case A.1: Return single value as-is
            # size_logo must be BrandLogoResource here since has_light_dark is False
            return logo_attach_attrs(cast(BrandLogoResource, size_logo), kwargs)

        # size_logo must be BrandLogoResourceLightDark here since has_light_dark is True
        light_dark_logo = cast(BrandLogoResourceLightDark, size_logo)
        if (
            light_dark_logo.light is not None
            and light_dark_logo.dark is not None
        ):
            # Case A.2: Return light_dark if both variants exist
            return logo_attach_attrs(light_dark_logo, kwargs)

        if light_dark_logo.light is not None:
            # Case A.3: Return light if only light exists
            return logo_attach_attrs(light_dark_logo.light, kwargs)

        if light_dark_logo.dark is not None:
            # Case A.4: Return dark if only dark exists
            return logo_attach_attrs(light_dark_logo.dark, kwargs)

    elif variant == "light_dark":
        if has_light_dark:
            # Case B.1: Return light_dark if both variants exist
            return logo_attach_attrs(
                cast(BrandLogoResourceLightDark, size_logo), kwargs
            )

        if allow_fallback:
            # Case B.2: Promote single to light_dark if fallback allowed
            # At this point we know size_logo is a single BrandLogoResource
            single_resource = cast(BrandLogoResource, size_logo)
            return logo_attach_attrs(
                BrandLogoResourceLightDark(
                    light=single_resource, dark=single_resource
                ),
                kwargs,
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
            light_dark_logo = cast(BrandLogoResourceLightDark, size_logo)
            variant_resource = getattr(light_dark_logo, variant, None)
            if variant_resource is not None:
                return logo_attach_attrs(variant_resource, kwargs)
        else:
            # Case D: return single if fallback allowed
            if allow_fallback:
                return logo_attach_attrs(
                    cast(BrandLogoResource, size_logo), kwargs
                )

        # Case X: specific variant doesn't exist and can't fallback
        if required_reason is not None:
            raise ValueError(
                f"brand.logo.{name}.{variant} is required{required_reason}."
            )
        return None


@overload
def logo_attach_attrs(
    logo: BrandLogoResource, attrs: dict[str, Any]
) -> BrandLogoResource: ...


@overload
def logo_attach_attrs(
    logo: BrandLogoResourceLightDark, attrs: dict[str, Any]
) -> BrandLogoResourceLightDark: ...


def logo_attach_attrs(
    logo: BrandLogoResource | BrandLogoResourceLightDark,
    attrs: dict[str, Any],
) -> BrandLogoResource | BrandLogoResourceLightDark:
    """Add attrs to a logo resource, preserving the original type."""
    if not attrs:
        return logo

    # Convert class_ to class for HTML compatibility
    processed_attrs = {}
    for key, value in attrs.items():
        if key == "class_":
            processed_attrs["class"] = value
        else:
            processed_attrs[key] = value

    # Check if this is a BrandLogoResourceLightDark (has light and dark attributes)
    if isinstance(logo, BrandLogoResourceLightDark):
        # Handle BrandLogoResourceLightDark - copy attrs to both variants
        light_attrs = (
            getattr(logo.light, "attrs", None) or {} if logo.light else {}
        )
        dark_attrs = (
            getattr(logo.dark, "attrs", None) or {} if logo.dark else {}
        )

        new_light = (
            logo.light.model_copy(
                update={"attrs": {**light_attrs, **processed_attrs}}
            )
            if logo.light
            else None
        )
        new_dark = (
            logo.dark.model_copy(
                update={"attrs": {**dark_attrs, **processed_attrs}}
            )
            if logo.dark
            else None
        )

        return BrandLogoResourceLightDark(light=new_light, dark=new_dark)
    else:
        # Handle single BrandLogoResource
        current_attrs = getattr(logo, "attrs", None) or {}
        new_attrs = {**current_attrs, **processed_attrs}
        return logo.model_copy(update={"attrs": new_attrs})
