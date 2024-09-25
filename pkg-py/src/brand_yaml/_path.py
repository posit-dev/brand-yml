from __future__ import annotations

from pathlib import Path

from pydantic import HttpUrl, RootModel


class FileLocation(RootModel):
    root: HttpUrl | Path
    _root_dir: Path

    def __init__(self, path: str | Path | HttpUrl):
        super().__init__(path)
        self._root_dir = Path(".").absolute()

    def __call__(self) -> Path | HttpUrl:
        if isinstance(self.root, Path):
            if self.root.is_absolute():
                return self.root
            return self._root_dir / self.root
        return self.root

    def _update_root_dir(self, root_dir: Path) -> bool:
        self._root_dir = root_dir
        return False

    def _validate_path_exists(self) -> bool:
        path = self()
        if not path or not isinstance(path, Path):
            return False

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return False
