from __future__ import annotations

from pathlib import Path
from typing import Union

from pydantic import HttpUrl, RootModel, field_validator


class FileLocation(RootModel):
    def __str__(self) -> str:
        return str(self.root)

    @field_validator("root")
    @classmethod
    def validate_root(cls, v: Path | HttpUrl) -> Path | HttpUrl:
        if isinstance(v, Path):
            v = Path(v).expanduser()

        vp = Path(str(v))
        if vp.suffix == "":
            raise ValueError(
                "Must be a path to a single file which must include an extension."
            )

        return v


class FileLocationUrl(FileLocation):
    root: HttpUrl


class FileLocationLocal(FileLocation):
    root: Path

    def make_absolute(self, relative_to: str | Path = Path(".")):
        if self.root.is_absolute():
            return

        relative_to = Path(relative_to).absolute()
        self.root = relative_to / self.root

    def make_relative(self, relative_to: str | Path = Path(".")):
        if not self.root.is_absolute():
            return

        relative_to = Path(relative_to).absolute()
        self.root = self.root.relative_to(relative_to)

    def validate_path_exists(self) -> None:
        if not self.root.exists():
            raise FileNotFoundError(f"File not found: {self.root}")


FileLocationLocalOrUrl = Union[FileLocationUrl, FileLocationLocal]
