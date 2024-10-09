from __future__ import annotations

import os
import textwrap
from pathlib import Path
from typing import Any, Callable, TypeVar

from pydantic import BaseModel, field_validator

from ._utils import find_project_file


class ExampleFile(BaseModel):
    path: Path
    name: str
    desc: str | None = None
    filename: str = "_brand.yml"

    @field_validator("path", mode="after")
    @classmethod
    def validate_path(cls, value: str | Path) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = find_project_file("examples", Path(__file__)) / path

        return path

    def str_tabset_lines(self):
        with self.path.open() as f:
            lines = f.readlines()

        description = (
            textwrap.dedent(self.desc or "").splitlines() if self.desc else [""]
        )

        return [
            "\n",
            f"###### {self.name}",
            *description,
            f'```{{.yaml filename="{self.filename}"}}',
            *[line.rstrip() for line in lines],
            "```\n",
        ]


FuncType = Callable[..., Any]
F = TypeVar("F", bound=FuncType)


class DocStringWithExample(str): ...


def add_example_yaml(
    *args: ExampleFile | dict[str, str | Path],
) -> Callable[[F], F]:
    arg_models = [
        ExampleFile.model_validate(arg) if isinstance(arg, dict) else arg
        for arg in args
    ]

    def _(func: F) -> F:
        if os.getenv("IN_QUARTODOC") != "true":
            return func

        if len(args) < 1:
            return func

        examples = ["::: {.panel-tabset}"]
        for arg in arg_models:
            examples += arg.str_tabset_lines()
        examples += [":::\n\n"]

        if func.__doc__ is None:
            func.__doc__ = ""

        doc = func.__doc__.replace("\n", "")
        indent = " " * (len(doc) - len(doc.lstrip()))
        nl_indent = "\n" + indent

        if isinstance(func.__doc__, DocStringWithExample):
            ex_header = "Examples" + nl_indent + "--------"
            before, after = func.__doc__.split(ex_header, 1)
            func.__doc__ = before + ex_header
        else:
            func.__doc__ += nl_indent + "Examples"
            func.__doc__ += nl_indent + "--------"
            after = None

        # Insert the example under the Examples heading
        func.__doc__ += nl_indent * 2
        func.__doc__ += nl_indent.join(examples)
        if after is not None:
            func.__doc__ += after

        func.__doc__ = DocStringWithExample(func.__doc__)
        return func

    return _
