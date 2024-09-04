from __future__ import annotations

import logging
from copy import deepcopy

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, TypeVar, Generic, Optional

T = TypeVar("T")


class BrandLightDark(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    light: T = None
    dark: T = None


class BrandLightDarkString(BrandLightDark[str]):
    pass


class BrandWith(BaseModel, Generic[T]):
    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
        populate_by_name=True,
        revalidate_instances="always",
    )

    with_: Optional[dict[str, T]] = Field(default=None, alias="with")

    def model_post_init(self, __context: Any) -> None:
        if self.with_ is None:
            return

        logging.debug("resolving with_ values")
        self._replace_with_recursively()

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        self._replace_with_recursively()

    def _replace_with_recursively(self, items: dict | BaseModel | None = None, level=0):
        if level > 50:
            logging.error("BrandWith recursion limit reached")
            return

        if items is None:
            items = self

        if not isinstance(items, (dict, BaseModel)):
            return

        if isinstance(items, BaseModel):
            items_keys = items.model_fields.keys()
        elif hasattr(items, "keys"):
            items_keys = items.keys()

        for key in items_keys:
            logging.debug(f"checking key {key}")

            if isinstance(items, BaseModel):
                value = getattr(items, key)
            elif isinstance(items, dict):
                value = items[key]

            if isinstance(value, str) and value in self.with_:
                logging.debug(f"replacing key {key}")
                if isinstance(items, BaseModel):
                    setattr(items, key, deepcopy(self.with_[value]))
                elif isinstance(items, dict):
                    items[key] = deepcopy(self.with_[value])
            elif isinstance(value, (dict, BaseModel)):
                # TODO: we may want to avoid recursing into child BrandWith instances
                logging.debug(f"recursing into {key}")
                self._replace_with_recursively(value, level + 1)
            else:
                logging.debug(
                    f"skipping {key}, not replaceable (or not a dict or pydantic model)"
                )
