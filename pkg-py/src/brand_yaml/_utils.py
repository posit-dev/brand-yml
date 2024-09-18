from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class BrandBase(BaseModel):
    def __repr_args__(self):
        fields = [f for f in self.model_fields.keys()]
        values = [getattr(self, f) for f in fields]
        return ((f, v) for f, v in zip(fields, values) if v is not None)


def find_project_file(filename: str, dir_: Path) -> Path:
    dir_og = dir_
    i = 0
    max_parents = 20

    while dir_ != dir_.parent and i < max_parents:
        if (dir_ / filename).exists():
            return dir_ / filename
        dir_ = dir_.parent
        i += 1

    raise FileNotFoundError(
        f"Could not find {filename} in {dir_og} or its parents."
    )
