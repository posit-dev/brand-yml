from __future__ import annotations

from copy import copy
from pathlib import Path
from typing import Any, Union

from pydantic import HttpUrl, RootModel, field_validator


class FileLocation(RootModel):
    """The base class for a file location, either a local or an online file."""

    def __str__(self) -> str:
        return str(self.root)

    @field_validator("root")
    @classmethod
    def _validate_root(cls, v: Path | HttpUrl) -> Path | HttpUrl:
        if isinstance(v, Path):
            v = Path(v).expanduser()

        vp = Path(str(v))
        if vp.suffix == "":
            raise ValueError(
                "Must be a path to a single file which must include an extension."
            )

        return v


class FileLocationUrl(FileLocation):
    """A hosted, online file location, i.e. a URL."""

    root: HttpUrl


class FileLocationLocal(FileLocation):
    """
    A local file location. When used in a `brand_yaml.Brand` instance, this
    class carries both the relative path to the file, relative to the source
    `_brand.yml`, and the absolute path of the file on disk.
    """

    # TODO @docs: Show method docs only once

    root: Path
    _root_dir: Path | None = None

    @field_validator("root", mode="after")
    @classmethod
    def _validate_not_absolute(cls, value: Path) -> Path:
        v = value.expanduser()
        if v.is_absolute():
            raise ValueError(
                "Local paths must be relative to the Brand YAML source file. "
                + f"Use 'file://{v}' if you are certain you want to use "
                + "an absolute path for a local file."
            )

        return value

    def __copy__(self):
        m = super().__copy__()
        m._root_dir = copy(self._root_dir)
        return m

    def __deepcopy__(self, memo: dict[int, Any] | None = None):
        m = super().__deepcopy__(memo)
        m._root_dir = copy(self._root_dir)
        return m

    def set_root_dir(self, root_dir: Path) -> None:
        """
        Update the root directory of this file location. In general, the root
        directory is the parent directory containing the source `brand.yml`
        file. If you relocate the file, this method can be used to update the
        new local file location.
        """
        self._root_dir = root_dir

    def absolute(self) -> Path:
        """
        Returns the absolute path to the file, relative to the root directory,
        which is most typically the directory containing the `_brand.yml` file.
        """
        if self.root.is_absolute():
            return self.root

        if self._root_dir is None:
            return self.root.absolute()

        relative_to = Path(self._root_dir).absolute()
        return relative_to / self.root

    def relative(self) -> Path:
        """
        Returns the relative path to the file as it would appear in the source
        `_brand.yml` file.
        """
        if not self.root.is_absolute() or self._root_dir is None:
            return self.root

        relative_to = Path(self._root_dir).absolute()
        return self.root.relative_to(relative_to)

    def exists(self) -> bool:
        """Check that the file exists at its absolute path."""
        return self.absolute().exists()

    def validate_exists(self) -> None:
        """
        Validate that the file exists at its absolute path.

        Raises
        ------
        FileNotFoundError
            Raises a `FileNotFoundError` if the file does not exist at its
            absolute path location.
        """
        if not self.exists():
            raise FileNotFoundError(
                f"File '{self.root}' not found at '{self.absolute()}'"
            )


FileLocationLocalOrUrl = Union[FileLocationUrl, FileLocationLocal]
