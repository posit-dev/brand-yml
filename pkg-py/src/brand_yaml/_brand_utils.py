from __future__ import annotations

from copy import deepcopy
from textwrap import indent
from typing import Any, Generic, Optional, TypeVar, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ._utils_logging import logger

T = TypeVar("T")


class BrandLightDark(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    light: T = None
    dark: T = None


class BrandLightDarkString(BrandLightDark[str]):
    pass


LeafNode = Union[str, float, int, bool, None]


def is_leaf_node(value: Any) -> bool:
    # Note: We treat iterables as leaf nodes
    return not isinstance(value, (dict, BaseModel))


class BrandWith(BaseModel, Generic[T]):
    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
        populate_by_name=True,
        revalidate_instances="always",
        validate_assignment=True,
    )

    with_: Optional[dict[str, T]] = Field(default=None, alias="with")

    @field_validator("with_", mode="after")
    @classmethod
    def validate_with_(cls, value: dict[str, T] | None) -> dict[str, T] | None:
        if value is None:
            return value

        check_circular_references(value, name="with")
        return value

    @model_validator(mode="after")
    def resolve_with_values(self, __context: Any) -> None:
        if self.with_ is None:
            return self

        logger.debug("resolving with_ values")
        self._replace_with_recursively()
        return self

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        if name != "with_":
            self._replace_with_recursively(value)

    def _get_with(self, key: str, level=0) -> object:
        """
        Finds `key` in `with_`, which may require recursively resolving nested
        values from `with_`.
        """
        if key not in self.with_:
            return key

        # Note that this is simplified by the fact that we've already confirmed
        # that no circular references exist in `with_`.

        with_value = deepcopy(self.with_[key])
        logger.debug(
            level_indent(f"key {key} is in with_ with value {with_value!r}", level)
        )

        if is_leaf_node(self.with_[key]):
            return with_value
        else:
            self._replace_with_recursively(with_value, level)
            return with_value

    def _replace_with_recursively(self, items: dict | BaseModel | None = None, level=0):
        if level > 50:
            logger.error("BrandWith recursion limit reached")
            return

        if items is None:
            items = self

        if not isinstance(items, (dict, BaseModel)):
            return

        for key in item_keys(items):
            value = get_value(items, key)

            if value is self.with_:
                # We replace `with_` when resolving sibling fields
                continue

            logger.debug(level_indent(f"inspecting key {key}", level))
            if isinstance(value, str) and value in self.with_:
                new_value = self._get_with(value, level + 1)
                logger.debug(
                    level_indent(
                        f"replacing key {key} with value from {value}: {new_value!r}",
                        level,
                    )
                )
                if isinstance(items, BaseModel):
                    setattr(items, key, new_value)
                elif isinstance(items, dict):
                    items[key] = new_value
            elif isinstance(value, (dict, BaseModel)):
                # TODO: we may want to avoid recursing into child BrandWith instances
                logger.debug(level_indent(f"recursing into {key}", level))
                self._replace_with_recursively(value, level + 1)
            else:
                logger.debug(
                    level_indent(
                        f"skipping {key}, not replaceable (or not a dict or pydantic model)",
                        level,
                    )
                )


def level_indent(x: str, level: int) -> str:
    return indent(x, ("." * level))


def item_keys(item: dict | BaseModel) -> list[str]:
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
    data: dict[str, object],
    current: object = None,
    seen: list[str] = None,
    path: list[str] = None,
    name: str = None,
):
    current = current if current is not None else data
    seen = seen if seen is not None else []
    path = path if path is not None else []

    if not isinstance(current, (dict, BaseModel)):
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

        if isinstance(value, str):  # implied value is also in data by above check
            seen_key = [*seen, *([key, value] if len(seen) == 0 else [value])]
            if value in seen:
                raise CircularReferenceError(seen_key, path_key, name)
            else:
                new_current = {k: v for k, v in data.items() if k == value}
                check_circular_references(data, new_current, seen_key, path_key, name)
        else:
            check_circular_references(data, value, seen, path_key, name)


class CircularReferenceError(Exception):
    def __init__(self, seen: list[str], path: list[str], name: str = None):
        self.seen = seen
        self.path = path
        self.name = name

        msg_name = "" if not name else f" in '{name}'"

        message = f'Circular reference detected{msg_name}.\nRefs    : {" -> ".join(seen)}\nVia path: {" -> ".join(path)}'
        super().__init__(message)
