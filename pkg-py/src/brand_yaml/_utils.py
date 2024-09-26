from __future__ import annotations

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


def find_project_brand_yaml(dir_: Path) -> Path:
    return find_project_file("_brand.yml", dir_, ("brand", "_brand"))


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
