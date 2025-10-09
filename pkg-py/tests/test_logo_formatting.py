"""Tests for logo formatting methods"""

from __future__ import annotations

import htmltools
import pytest
from brand_yml import Brand
from brand_yml._defs import BrandLightDark
from brand_yml.logo import (
    BrandLogoResource,
    BrandLogoResourceLightDark,
    html_dep_brand_light_dark,
)


class TestBrandLogoResourceFormatting:
    """Test formatting methods for BrandLogoResource"""

    @pytest.fixture
    def basic_brand(self):
        """Brand with basic logo configuration"""
        return Brand.from_yaml_str("""
        logo:
          small:
            path: test.png
            alt: Test Logo
        """)

    @pytest.fixture
    def basic_logo(self, basic_brand):
        """Basic logo resource"""
        logo = basic_brand.use_logo("small")
        assert isinstance(logo, BrandLogoResource)
        return logo

    @pytest.fixture
    def brand_with_attrs(self):
        """Brand with custom attributes"""
        return Brand.from_yaml_str("""
        logo:
          small:
            path: test.png
            attrs:
              class: custom-class
        """)

    @pytest.fixture
    def simple_brand(self):
        """Brand with minimal logo configuration"""
        return Brand.from_yaml_str("""
        logo:
          small: test.png
        """)

    @pytest.fixture
    def simple_logo(self, simple_brand):
        """Simple logo resource"""
        logo = simple_brand.use_logo("small")
        assert isinstance(logo, BrandLogoResource)
        return logo

    def test_to_markdown_basic(self, basic_logo):
        """Test basic markdown output"""
        md = basic_logo.to_markdown()

        # Should contain markdown image syntax
        assert "![](data:" in md or "![](test.png)" in md
        assert ".brand-logo" in md
        assert 'alt="Test Logo"' in md

    def test_to_markdown_with_attrs(self, brand_with_attrs):
        """Test markdown output with additional attributes"""
        logo = brand_with_attrs.use_logo("small")
        assert isinstance(logo, BrandLogoResource)
        md = logo.to_markdown(width="100")

        assert ".brand-logo" in md
        assert ".custom-class" in md
        assert 'width="100"' in md

    def test_to_str_formats(self, simple_logo):
        """Test to_str with different formats"""
        # Default should be HTML
        html_str = simple_logo.to_str()
        assert html_str.startswith("<img")

        # Explicit HTML
        html_str2 = simple_logo.to_str(format_type="html")
        assert html_str2.startswith("<img")

        # Markdown
        md_str = simple_logo.to_str(format_type="markdown")
        assert md_str.startswith("![")

        # Invalid format
        with pytest.raises(ValueError, match="format_type must be"):
            simple_logo.to_str(format_type="invalid")

    def test_tagify_convenience(self, simple_logo):
        """Test tagify convenience method"""
        html1 = simple_logo.tagify()
        html2 = simple_logo.to_html()

        # Should be identical
        assert html1 == html2

    def test_str_method(self, simple_logo):
        """Test __str__ method defaults to markdown"""
        str_output = str(simple_logo)
        md_output = simple_logo.to_markdown()

        assert str_output == md_output

    def test_attrs_as_markdown(self, simple_logo):
        """Test _attrs_as_markdown helper"""
        # Test class handling
        attrs = {"class": "class1 class2", "width": "100", "alt": "Alt text"}
        formatted = simple_logo._attrs_as_markdown(attrs)

        assert ".class1" in formatted
        assert ".class2" in formatted
        assert 'width="100"' in formatted
        assert 'alt="Alt text"' in formatted


class TestBrandLogoResourceLightDarkFormatting:
    """Test formatting methods for BrandLogoResourceLightDark"""

    @pytest.fixture
    def light_dark_brand(self):
        """Brand with light/dark logo configuration"""
        return Brand.from_yaml_str("""
        logo:
          medium:
            light: light.png
            dark: dark.png
        """)

    @pytest.fixture
    def light_dark_logo(self, light_dark_brand):
        """Light/dark logo resource"""
        logo = light_dark_brand.use_logo("medium")
        assert isinstance(logo, BrandLogoResourceLightDark)
        return logo

    def test_to_html_light_dark(self, light_dark_logo):
        """Test HTML output for light/dark logo"""
        html = light_dark_logo.to_html()

        # Should contain span wrapper
        assert '<span class="brand-logo-light-dark">' in str(html)
        # Should contain both images
        assert "light-content" in str(html)
        assert "dark-content" in str(html)

    def test_to_markdown_light_dark(self, light_dark_logo):
        """Test markdown output for light/dark logo"""
        md = light_dark_logo.to_markdown()

        # Should contain both images
        assert ".light-content" in md
        assert ".dark-content" in md
        # Should have two separate image tags
        assert md.count("![") == 2

    def test_to_str_light_dark(self, light_dark_logo):
        """Test to_str with light/dark logo"""
        # HTML format
        html_str = light_dark_logo.to_str(format_type="html")
        assert "brand-logo-light-dark" in html_str

        # Markdown format
        md_str = light_dark_logo.to_str(format_type="markdown")
        assert ".light-content" in md_str
        assert ".dark-content" in md_str

    def test_str_method_light_dark(self, light_dark_logo):
        """Test __str__ method for light/dark logo"""
        str_output = str(light_dark_logo)
        md_output = light_dark_logo.to_markdown()

        assert str_output == md_output

    def test_type_checking(self):
        """Test type checking for non-logo resources"""
        # Create a BrandLightDark with non-logo content
        light_dark = BrandLightDark(light="not a logo", dark="also not a logo")

        # BrandLightDark should not have formatting methods
        assert not hasattr(light_dark, "to_html")
        assert not hasattr(light_dark, "to_markdown")


class TestFormattingIntegration:
    """Test integration between use_logo and formatting"""

    @pytest.fixture
    def brand_with_base_class(self):
        """Brand with base class in attrs"""
        return Brand.from_yaml_str("""
        logo:
          small:
            path: test.png
            attrs:
              class: base-class
        """)

    @pytest.fixture
    def light_dark_brand(self):
        """Brand with light/dark logo configuration"""
        return Brand.from_yaml_str("""
        logo:
          medium:
            light: light.png
            dark: dark.png
        """)

    @pytest.fixture
    def multi_logo_brand(self):
        """Brand with both single and light/dark logos"""
        return Brand.from_yaml_str("""
        logo:
          small: test.png
          medium:
            light: light.png
            dark: dark.png
        """)

    def test_use_logo_with_formatting_attrs(self, brand_with_base_class):
        """Test that attrs from use_logo are properly passed to formatting"""
        # Add attrs via use_logo
        logo = brand_with_base_class.use_logo(
            "small", width="200", class_="extra-class"
        )
        assert isinstance(logo, BrandLogoResource)
        assert logo.attrs is not None

        # Check that attrs are combined
        assert logo.attrs["width"] == "200"
        assert logo.attrs["class"] == "base-class extra-class"

        # Test in HTML output
        html = logo.to_html()
        assert 'width="200"' in str(html)
        assert 'class="brand-logo base-class extra-class"' in str(html)

    def test_light_dark_attrs_propagation(self, light_dark_brand):
        """Test that attrs are properly propagated to light/dark variants"""
        logo = light_dark_brand.use_logo("medium", width="150")
        assert isinstance(logo, BrandLogoResourceLightDark)
        html = logo.to_html()

        # Both variants should have the width
        assert str(html).count('width="150"') == 2
        # Both should have their respective content classes
        assert "light-content" in str(html)
        assert "dark-content" in str(html)

    def test_jupyter_repr_html(self, multi_logo_brand):
        """Test _repr_html_ for Jupyter integration"""
        # Single resource
        logo = multi_logo_brand.use_logo("small")
        assert isinstance(logo, BrandLogoResource)
        repr_html = logo._repr_html_()
        assert repr_html.startswith("<img")

        # Light/dark resource
        logo_ld = multi_logo_brand.use_logo("medium")
        assert isinstance(logo_ld, BrandLogoResourceLightDark)
        repr_html_ld = logo_ld._repr_html_()
        assert "brand-logo-light-dark" in repr_html_ld

    def test_html_dependency_inclusion(self, multi_logo_brand):
        """Test that HTML dependencies are included"""
        logo = multi_logo_brand.use_logo("small")
        assert isinstance(logo, BrandLogoResource)
        html = logo.to_html()

        assert isinstance(html, htmltools.Tag)
        assert html.get_dependencies() == [html_dep_brand_light_dark()]
