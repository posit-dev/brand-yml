from __future__ import annotations

from pydantic import BaseModel


class BrandBase(BaseModel):
    def __repr_args__(self):
        fields = [f for f in self.model_fields.keys()]
        values = [getattr(self, f) for f in fields]
        return ((f, v) for f, v in zip(fields, values) if v is not None)
