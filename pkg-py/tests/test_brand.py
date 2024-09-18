import tempfile
from pathlib import Path

import pytest
from brand_yaml import read_brand_yaml


def test_brand_yml_found_in_dir():
    path = Path(__file__).parent / "fixtures" / "find-brand-yml" / "_brand.yml"

    brand_direct = read_brand_yaml(path)
    brand_found = read_brand_yaml(path.parent)

    assert brand_found == brand_direct


def test_brand_yml_found_from_py_file():
    path = Path(__file__).parent / "fixtures" / "find-brand-yml" / "_brand.yml"

    brand_direct = read_brand_yaml(path)
    # Equivalent to passing __file__ from inside empty.py
    brand_found = read_brand_yaml(path.parent / "empty.py")

    assert brand_found == brand_direct


def test_brand_yml_not_found_error():
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(FileNotFoundError):
            read_brand_yaml(tmpdir)
