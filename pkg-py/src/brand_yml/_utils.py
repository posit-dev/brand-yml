from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, List, Union

from pydantic import BaseModel


def find_project_file(
    filename: str,
    dir_: Path,
    subdir: tuple[str, ...] = (),
) -> Path:
    dir_og = dir_
    i = 0
    max_parents = 20

    while dir_ != dir_.parent and i < max_parents:
        if (dir_ / filename).exists():
            return dir_ / filename
        for sub in subdir:
            if (dir_ / sub / filename).exists():
                return dir_ / sub / filename
        dir_ = dir_.parent
        i += 1

    raise FileNotFoundError(
        f"Could not find {filename} in {dir_og} or its parents."
    )


def find_project_brand_yml(path: Path | str) -> Path:
    """
    Find a project's `_brand.yml` file

    Finds the first `_brand.yml` file in or adjacent to `path` and its parents.
    If `path` is a file, `find_project_brand_yml()` starts looking in the path's
    parent directory. In each directory, `find_project_brand_yml()` looks for
    any of the following files in the given order:

    * `_brand.yml`
    * `brand/_brand.yml`
    * `_brand/_brand.yml`

    Parameters
    ----------
    path
        A path to a file or directory where the search for the project's
        `_brand.yml` file should be located.

    Returns
    -------
    :
        The path of the found `_brand.yml`.

    Raises
    ------
    FileNotFoundError
        If no `_brand.yml` is found in any of the directories above `path`.
    """
    path = Path(path)
    path = path.resolve()

    if path.is_file():
        path = path.parent

    return find_project_file("_brand.yml", path, ("brand", "_brand"))


PredicateFuncType = Callable[[Any], bool]
ModifyFuncType = Callable[[Any], Union[bool, None]]


def recurse_dicts_and_models(
    item: Dict[str, Any] | BaseModel | List[Any],
    pred: PredicateFuncType,
    modify: ModifyFuncType,
) -> None:
    """
    Recursively traverse a nested structure of dictionaries, lists, and Pydantic
    models and apply an in-place modification when a node in the nested
    structure matches a predicate function.

    Parameters
    ----------
    item
        The nested structure to traverse. This can be a dictionary, list, or
        Pydantic model.

    pred
        A function that takes an item and returns a boolean indicating whether
        the item should be modified.

    modify
        A function that takes an item, modifies it in place, and returns a
        boolean indicating whether the traversal should continue to recurse into
        the item.

    Returns
    -------
    :
        Nothing, the function modifies the input `item` in place.
    """

    def apply(value: Any):
        if pred(value):
            should_recurse = modify(value)
            if should_recurse:
                recurse_dicts_and_models(value, pred, modify)
        else:
            recurse_dicts_and_models(value, pred, modify)

    if isinstance(item, BaseModel):
        for field in item.model_fields.keys():
            value = getattr(item, field)
            apply(value)

    elif isinstance(item, dict):
        for value in item.values():
            apply(value)

    elif isinstance(item, list):
        for value in item:
            apply(value)


@contextmanager
def set_env_var(key: str, value: str):
    original_value = os.environ.get(key)
    os.environ[key] = value
    try:
        yield
    finally:
        if original_value is not None:
            os.environ[key] = original_value
        else:
            del os.environ[key]


@contextmanager
def maybe_default_font_source(value: str | None):
    """
    Safely update the default font source if one is provided.

    The default follows the `BRAND_YML_DEFAULT_FONT_SOURCE` envvar, which will
    be masked within this context if `value` is not `None`.
    """
    key = "BRAND_YML_DEFAULT_FONT_SOURCE"
    if value is not None:
        with set_env_var(key, value):
            yield
    else:
        yield
