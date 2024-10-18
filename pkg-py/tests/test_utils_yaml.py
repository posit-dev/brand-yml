from __future__ import annotations

from brand_yml import Brand


def test_brand_model_dump_yaml(snapshot):
    brand = Brand.from_yaml_str("""
    meta:
      name: Brand YAML
    color:
      palette:
        orange: "#ff9a02"
      primary: orange
    typography:
      headings: Raleway
    """)

    assert snapshot == brand.model_dump_yaml()
