from __future__ import annotations

import os

import pytest
from brand_yml import Brand, BrandColor
from brand_yml._utils import envvar_brand_yml_path


@pytest.fixture
def brand_yml_file(tmp_path):
    """Create a temporary brand.yml file for testing."""
    yml_content = """
color:
  palette:
    blue: '#0000FF'
  primary: blue
"""
    brand_yml_path = tmp_path / "_brand.yml"
    brand_yml_path.write_text(yml_content)
    return brand_yml_path


class TestEnvVarBrandYmlPath:
    """Test the BRAND_YML_PATH environment variable functionality."""

    def test_envvar_brand_yml_path_not_set(self):
        """Test that envvar_brand_yml_path() returns None when BRAND_YML_PATH is not set."""
        if "BRAND_YML_PATH" in os.environ:
            del os.environ["BRAND_YML_PATH"]

        assert envvar_brand_yml_path() is None

    def test_envvar_brand_yml_path_set(self, tmp_path):
        """Test that envvar_brand_yml_path() returns the path when BRAND_YML_PATH is set."""
        test_path = tmp_path / "test_brand.yml"
        os.environ["BRAND_YML_PATH"] = str(test_path)

        try:
            result = envvar_brand_yml_path()
            assert result == test_path.resolve()
        finally:
            # Clean up environment
            del os.environ["BRAND_YML_PATH"]

    def test_brand_from_yaml_with_envvar(self, brand_yml_file):
        """Test that Brand.from_yaml() uses BRAND_YML_PATH when path is None."""
        os.environ["BRAND_YML_PATH"] = str(brand_yml_file)

        try:
            brand = Brand.from_yaml()
            assert brand.path == brand_yml_file.resolve()
            assert isinstance(brand, Brand)
            assert isinstance(brand.color, BrandColor)
            assert brand.color.primary == "#0000FF"
        finally:
            # Clean up environment
            del os.environ["BRAND_YML_PATH"]

    def test_brand_from_yaml_no_path_no_envvar(self):
        """Test that Brand.from_yaml() raises ValueError when path is None and BRAND_YML_PATH is not set."""
        if "BRAND_YML_PATH" in os.environ:
            del os.environ["BRAND_YML_PATH"]

        with pytest.raises(
            ValueError,
            match="No path specified and the BRAND_YML_PATH environment variable is not set",
        ):
            Brand.from_yaml()

    def test_path_param_overrides_envvar(self, brand_yml_file, tmp_path):
        """Test that explicitly provided path overrides BRAND_YML_PATH."""
        # Create another brand file with different content
        other_path = tmp_path / "other_brand.yml"
        other_path.write_text("""
color:
  palette:
    red: '#FF0000'
  primary: red
""")

        # Set environment variable to one path
        os.environ["BRAND_YML_PATH"] = str(other_path)

        try:
            # But use the other path explicitly in from_yaml
            brand = Brand.from_yaml(brand_yml_file)

            # Should use the explicitly provided path, not the env var
            assert brand.path == brand_yml_file.resolve()
            assert isinstance(brand, Brand)
            assert isinstance(brand.color, BrandColor)
            assert brand.color.primary == "#0000FF"
        finally:
            # Clean up environment
            del os.environ["BRAND_YML_PATH"]

    def test_envvar_with_home_dir_expansion(self, monkeypatch, tmp_path):
        """Test that ~ is expanded in BRAND_YML_PATH."""
        # Mock home directory to be the tmp_path
        monkeypatch.setenv("HOME", str(tmp_path))

        # Create a brand file in the mock home directory
        home_brand_path = tmp_path / "home_brand.yml"
        home_brand_path.write_text("""
color:
  palette:
    green: '#00FF00'
  primary: green
""")

        # Set environment variable with ~ in the path
        os.environ["BRAND_YML_PATH"] = "~/home_brand.yml"

        try:
            # Should expand ~ to the mock home directory
            brand = Brand.from_yaml()
            assert brand.path == home_brand_path.resolve()
            assert isinstance(brand, Brand)
            assert isinstance(brand.color, BrandColor)
            assert brand.color.primary == "#00FF00"
        finally:
            # Clean up environment
            del os.environ["BRAND_YML_PATH"]
