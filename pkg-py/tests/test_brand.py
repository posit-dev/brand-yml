import tempfile
from pathlib import Path

import pytest
from brand_yaml import read_brand_yaml
from brand_yaml.file import FileLocationLocal
from brand_yaml.logo import BrandLogo
from brand_yaml.typography import BrandTypography, BrandTypographyFontFiles

path_fixtures = Path(__file__).parent / "fixtures"


def test_brand_yml_found_in_dir():
    path = path_fixtures / "find-brand-yml" / "_brand.yml"

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


def test_brand_yml_paths():
    path = path_fixtures / "path-resolution"

    # This doesn't error, even though it points to missing files
    brand = read_brand_yaml(path)

    assert isinstance(brand.logo, BrandLogo)

    assert isinstance(brand.typography, BrandTypography)
    assert isinstance(brand.typography.fonts, list)
    assert isinstance(brand.typography.fonts[0], BrandTypographyFontFiles)

    # Paths are all relative initially
    assert str(brand.logo.small) == "does-not-exist.png"
    assert str(brand.typography.fonts[0].files[0].path) == "Invisible.ttf"

    # but can be made absolute with a method call
    brand.paths_make_absolute()
    assert isinstance(brand.logo.small, FileLocationLocal)
    assert brand.logo.small.root == path.absolute() / "does-not-exist.png"
    assert isinstance(
        brand.typography.fonts[0].files[0].path,
        FileLocationLocal,
    )
    assert (
        brand.typography.fonts[0].files[0].path.root
        == path.absolute() / "Invisible.ttf"
    )

    # which can be reversed again back to relative paths (possibly destructive)
    brand.paths_make_relative()
    assert str(brand.logo.small) == "does-not-exist.png"
    assert str(brand.typography.fonts[0].files[0].path) == "Invisible.ttf"
