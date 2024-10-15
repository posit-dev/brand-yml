"""
Base Pydantic model for Brand-related classes.
"""

from __future__ import annotations

from pydantic import BaseModel


class BrandBase(BaseModel):
    """
    A base model for brand-related data.

    This class inherits from Pydantic's BaseModel and provides a basic structure
    that can be extended with additional fields as needed. Currently, its
    primary purpose is to standardize the printed format of brand classes.
    """

    def __repr_args__(self):
        """
        Automatically exclude arguments whose values are `None` from the
        representation string.
        """
        fields = [f for f in self.model_fields.keys()]
        values = [getattr(self, f) for f in fields]
        return ((f, v) for f, v in zip(fields, values) if v is not None)
