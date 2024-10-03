from __future__ import annotations

from copy import deepcopy
from textwrap import indent
from typing import Any, Generic, Iterable, TypeVar, Union

from pydantic import (
    BaseModel,
    ConfigDict,
)

from ._utils_logging import logger

DictString = dict[str, str]
DictStringRecursive = Union[DictString, dict[str, "DictStringRecursive"]]
DictStringRecursiveBaseModel = Union[DictStringRecursive, dict[str, BaseModel]]

T = TypeVar("T")


class BrandLightDark(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    light: T | None = None
    dark: T | None = None


def is_leaf_node(value: Any) -> bool:
    # Note: We treat iterables as leaf nodes
    return not isinstance(value, (dict, BaseModel))


def defs_get(
    defs: DictStringRecursiveBaseModel,
    key: str,
    level: int = 0,
) -> object:
    """
    Finds `key` in `deps`, which may require recursively resolving nested
    values in `deps`.

    Parameters
    ----------

    defs
        A dictionary of definitions.

    key
        The key to look up in `defs`.

    Returns
    -------
    :
        The a deep copy of the value of `key` in `defs`, with any internal
        references to top-level keys in `defs` also resolved. If `defs[key]`
        returns a dictionary or pydantic model, internal references to
        definitions are also replaced.
    """
    if key not in defs:
        return key

    # Note that we assume that `defs` has already been checked for circular
    # references, so we don't need to check for them here.

    with_value = deepcopy(defs[key])
    logger.debug(
        level_indent(f"key {key} is in defs with value {with_value!r}", level)
    )

    if isinstance(with_value, (dict, BaseModel)):
        defs_replace_recursively(with_value, defs=defs, level=level)
        return with_value
    else:
        return with_value


def defs_replace_recursively(
    items: dict | BaseModel | None,
    defs: dict | None = None,
    level: int = 0,
    name: str | None = None,
    exclude: str | None = None,
):
    """
    Recursively replace string values in `items` with their definition in
    `defs`. An item in `items` is replaced if it is a string and exactly matches
    a key in the `defs` dictionary. Definitions in `defs` can refer to other
    definitions, provided that no definitions are circular, e.g. `a -> b -> a`.

    Parameters
    ----------
    items
        A dictionary or pydantic model in which values should be replaced.

    defs
        A dictionary of definitions.

    level
        The current recursion level. Used internally and for logging.

    Returns
    -------
    :
        Nothing. `items` is modified in place. Note that when values in items
        refer to definitions in `defs`, the are replaced with copies of the
        definition.
    """
    if items is None:
        return None

    if defs is None:
        if isinstance(items, dict):
            defs = items
        else:  # pragma: no cover
            raise ValueError(
                "When `defs` is `None`, `items` must be a dictionary."
            )

    if level == 0:
        logger.debug("Checking for circular references")
        check_circular_references(defs, name=name)

    if level > 50:  # pragma: no cover
        logger.error("Hit recursion limit recursing into `items`")
        return

    for key in item_keys(items):
        value = get_value(items, key)

        if value is defs or key in set((exclude or "with_", "with_")):
            # We replace internal def references when resolving sibling fields
            continue

        logger.debug(level_indent(f"inspecting key {key}", level))
        if isinstance(value, str) and value in defs:
            new_value = defs_get(defs, value, level=level + 1)
            logger.debug(
                level_indent(
                    f"replacing key {key} with definition from {value}: {new_value!r}",
                    level,
                )
            )
            if isinstance(items, BaseModel):
                setattr(items, key, new_value)
            elif isinstance(items, dict):
                items[key] = new_value
        elif isinstance(value, (dict, BaseModel)):
            logger.debug(level_indent(f"recursing into {key}", level))
            defs_replace_recursively(
                value,
                defs=defs,
                level=level + 1,
                exclude=exclude,
                name=name,
            )
        else:
            logger.debug(
                level_indent(
                    f"skipping {key}, not replaceable (or not a dict or pydantic model)",
                    level,
                )
            )


def level_indent(x: str, level: int) -> str:
    return indent(x, ("." * level))


def item_keys(item: DictStringRecursiveBaseModel | BaseModel) -> Iterable[str]:
    if isinstance(item, BaseModel):
        return item.model_fields.keys()
    elif hasattr(item, "keys"):
        return item.keys()
    else:
        return []


def get_value(items: dict | BaseModel, key: str) -> object:
    if isinstance(items, BaseModel):
        return getattr(items, key)
    elif isinstance(items, dict):
        return items[key]


def check_circular_references(
    data: dict[str, Any],
    current: object | None = None,
    seen: list[str] | None = None,
    path: list[str] | None = None,
    name: str | None = None,
):
    current = current if current is not None else data
    seen = seen if seen is not None else []
    path = path if path is not None else []

    if not isinstance(current, (dict, BaseModel)):  # pragma: no cover
        if not isinstance(current, str):
            raise ValueError(
                "All values must be strings, dictionaries, or pydantic models."
            )
        return

    logger.debug(f"current is: {current}")
    logger.debug(f"seen is: {seen}")
    logger.debug(f"path is: {path}")

    for key in item_keys(current):
        value = get_value(current, key)

        # Pass through objects we can recurse or strings if they're keys in `data`
        if isinstance(value, str):
            if value not in data:
                continue
        elif is_leaf_node(value):
            continue

        path_key = [*path, key]

        # implied value is also in data by above check
        if isinstance(value, str):
            seen_key = [*seen, *([key, value] if len(seen) == 0 else [value])]
            if value in seen:
                raise CircularReferenceError(seen_key, path_key, name)
            else:
                new_current = {k: v for k, v in data.items() if k == value}
                check_circular_references(
                    data, new_current, seen_key, path_key, name
                )
        else:
            check_circular_references(data, value, seen, path_key, name)


class CircularReferenceError(Exception):
    def __init__(
        self,
        seen: list[str],
        path: list[str],
        name: str | None = None,
    ):
        self.seen = seen
        self.path = path
        self.name = name

        msg_name = "" if not name else f" in '{name}'"

        message = f'Circular reference detected{msg_name}.\nRefs    : {" -> ".join(seen)}\nVia path: {" -> ".join(path)}'
        super().__init__(message)
