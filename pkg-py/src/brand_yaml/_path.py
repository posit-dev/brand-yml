from __future__ import annotations

from pathlib import Path

from pydantic import HttpUrl, RootModel


class FileLocation(RootModel):
    root: HttpUrl | Path
    _root_dir: Path | None = None

    def __init__(self, path: str | Path | HttpUrl):
        super().__init__(path)

    def __call__(self) -> Path | HttpUrl:
        if self._root_dir is None:
            return self.root

        if isinstance(self.root, Path):
            if self.root.is_absolute():
                return self.root
            return self._root_dir / self.root

        return self.root

    def set_root_dir(self, root_dir: Path, validate_path: bool = False) -> None:
        self._root_dir = root_dir

        if validate_path:
            self._validate_path_exists()

    def _validate_path_exists(self) -> None:
        path = self()
        if not path or not isinstance(path, Path):
            return

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
