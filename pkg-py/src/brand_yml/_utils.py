from __future__ import annotations

import os
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, List, Union

from pydantic import BaseModel

rgx_css_value_unit = re.compile(r"^(-?\d*\.?\d+)\s*([a-zA-Z%]*)$")


def envvar_brand_yml_path() -> Path | None:
    """
    Get the path to a brand.yml file from the `BRAND_YML_PATH` environment
    variable, if it is set.

    Returns
    -------
    :
        The path to the brand.yml file, or `None` if the environment variable
        is not set.
    """
    envvar = os.getenv("BRAND_YML_PATH")
    if envvar:
        return Path(envvar).expanduser().resolve()
    return None


def find_project_file(
    filename: tuple[str, ...] | str,
    dir_: Path,
    subdir: tuple[str, ...] = (),
) -> Path:
    dir_og = dir_
    i = 0
    max_parents = 20

    if isinstance(filename, str):
        filename = tuple([filename])

    while dir_ != dir_.parent and i < max_parents:
        for fname in filename:
            if (dir_ / fname).exists():
                return dir_ / fname
        for sub in subdir:
            for fname in filename:
                if (dir_ / sub / fname).exists():
                    return dir_ / sub / fname
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
    * `_brand.yaml`
    * `brand/_brand.yml`
    * `brand/_brand.yaml`
    * `_brand/_brand.yml`
    * `_brand/_brand.yaml`

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

    return find_project_file(
        filename=("_brand.yml", "_brand.yaml"),
        dir_=path,
        subdir=("brand", "_brand"),
    )


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
        for field in item.__class__.model_fields.keys():
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


def maybe_convert_font_size_to_rem(x: str) -> str:
    """
    Convert a font size to rem

    Some frameworks, like Bootstrap expect base font size to be in `rem`. This
    function converts `em`, `%`, `px`, `pt` to `rem`:

    1. `em` is directly replace with `rem`.
    2. `1%` is `0.01rem`, e.g. `90%` becomes `0.9rem`.
    3. `16px` is `1rem`, e.g. `18px` becomes `1.125rem`.
    4. `12pt` is `1rem`.
    5. `0.1666in` is `1rem`.
    6. `4.234cm` is `1rem`.
    7. `42.3mm` is `1rem`.
    """
    x_og = f"{x}"

    value, unit = split_css_value_and_unit(x)

    if unit == "rem":
        return x

    if unit == "em":
        return f"{value}rem"

    scale = {
        "%": 100,
        "px": 16,
        "pt": 12,
        "in": 16 / 96,  # 96 px/inch
        "cm": 16 / 96 * 2.54,  # inch -> cm
        "mm": 16 / 96 * 25.4,  # cm -> mm
    }

    if unit in scale:
        ret = f"{float(value) / scale[unit]:.4f}rem".replace(".0000", "")
        ret = re.sub("[.]?0+rem", "rem", ret)
        return ret

    raise ValueError(
        f"Could not convert font size {x_og!r} from {unit} units to a relative unit."
    )


def split_css_value_and_unit(x: str) -> tuple[str, str]:
    match = rgx_css_value_unit.match(x)
    if not match:
        raise ValueError(f"Invalid CSS value format: {x}")
    value, unit = match.groups()
    return value, unit
