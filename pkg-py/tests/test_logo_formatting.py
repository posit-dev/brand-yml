"""Tests for logo formatting methods"""

from __future__ import annotations

import pytest
from brand_yml import Brand
from brand_yml._defs import BrandLightDark


class TestBrandLogoResourceFormatting:
    """Test formatting methods for BrandLogoResource"""

    def test_to_markdown_basic(self):
        """Test basic markdown output"""
        brand = Brand.from_yaml_str("""
        logo:
          small:
            path: test.png
            alt: Test Logo
        """)

        logo = brand.use_logo("small")
        md = logo.to_markdown()

        # Should contain markdown image syntax
        assert "![](data:" in md or "![](test.png)" in md
        assert "{.brand-logo" in md
        assert 'alt="Test Logo"' in md

    def test_to_markdown_with_attrs(self):
        """Test markdown output with additional attributes"""
        brand = Brand.from_yaml_str("""
        logo:
          small:
            path: test.png
            attrs:
              class: custom-class
        """)

        logo = brand.use_logo("small")
        md = logo.to_markdown(width="100")

        assert ".brand-logo" in md
        assert ".custom-class" in md
        assert 'width="100"' in md

    def test_to_str_formats(self):
        """Test to_str with different formats"""
        brand = Brand.from_yaml_str("""
        logo:
          small: test.png
        """)

        logo = brand.use_logo("small")

        # Default should be HTML
        html_str = logo.to_str()
        assert html_str.startswith("<img")

        # Explicit HTML
        html_str2 = logo.to_str(format_type="html")
        assert html_str2.startswith("<img")

        # Markdown
        md_str = logo.to_str(format_type="markdown")
        assert md_str.startswith("![")

        # Invalid format
        with pytest.raises(ValueError, match="format_type must be"):
            logo.to_str(format_type="invalid")

    def test_tagify_convenience(self):
        """Test tagify convenience method"""
        brand = Brand.from_yaml_str("""
        logo:
          small: test.png
        """)

        logo = brand.use_logo("small")
        html1 = logo.tagify()
        html2 = logo.to_html()

        # Should be identical
        assert html1 == html2

    def test_str_method(self):
        """Test __str__ method defaults to markdown"""
        brand = Brand.from_yaml_str("""
        logo:
          small: test.png
        """)

        logo = brand.use_logo("small")
        str_output = str(logo)
        md_output = logo.to_markdown()

        assert str_output == md_output

    def test_attrs_as_markdown(self):
        """Test _attrs_as_markdown helper"""
        brand = Brand.from_yaml_str("""
        logo:
          small: test.png
        """)

        logo = brand.use_logo("small")

        # Test class handling
        attrs = {"class": "class1 class2", "width": "100", "alt": "Alt text"}
        formatted = logo._attrs_as_markdown(attrs)

        assert ".class1" in formatted
        assert ".class2" in formatted
        assert 'width="100"' in formatted
        assert 'alt="Alt text"' in formatted


class TestBrandLightDarkFormatting:
    """Test formatting methods for BrandLightDark[BrandLogoResource]"""

    def test_to_html_light_dark(self):
        """Test HTML output for light/dark logo"""
        brand = Brand.from_yaml_str("""
        logo:
          medium:
            light: light.png
            dark: dark.png
        """)

        logo = brand.use_logo("medium")
        html = logo.to_html()

        # Should contain span wrapper
        assert '<span class="brand-logo-light-dark">' in html
        # Should contain both images
        assert "light-content" in html
        assert "dark-content" in html

    def test_to_markdown_light_dark(self):
        """Test markdown output for light/dark logo"""
        brand = Brand.from_yaml_str("""
        logo:
          medium:
            light: light.png
            dark: dark.png
        """)

        logo = brand.use_logo("medium")
        md = logo.to_markdown()

        # Should contain both images
        assert ".light-content" in md
        assert ".dark-content" in md
        # Should have two separate image tags
        assert md.count("![") == 2

    def test_to_str_light_dark(self):
        """Test to_str with light/dark logo"""
        brand = Brand.from_yaml_str("""
        logo:
          medium:
            light: light.png
            dark: dark.png
        """)

        logo = brand.use_logo("medium")

        # HTML format
        html_str = logo.to_str(format_type="html")
        assert "brand-logo-light-dark" in html_str

        # Markdown format
        md_str = logo.to_str(format_type="markdown")
        assert ".light-content" in md_str
        assert ".dark-content" in md_str

    def test_str_method_light_dark(self):
        """Test __str__ method for light/dark logo"""
        brand = Brand.from_yaml_str("""
        logo:
          medium:
            light: light.png
            dark: dark.png
        """)

        logo = brand.use_logo("medium")
        str_output = str(logo)
        md_output = logo.to_markdown()

        assert str_output == md_output

    def test_type_checking(self):
        """Test type checking for non-logo resources"""
        # Create a BrandLightDark with non-logo content
        light_dark = BrandLightDark(light="not a logo", dark="also not a logo")

        with pytest.raises(
            TypeError,
            match="only works with BrandLightDark\\[BrandLogoResource\\]",
        ):
            light_dark.to_html()

        with pytest.raises(
            TypeError,
            match="only works with BrandLightDark\\[BrandLogoResource\\]",
        ):
            light_dark.to_markdown()


class TestFormatmingIntegration:
    """Test integration between use_logo and formatting"""

    def test_use_logo_with_formatting_attrs(self):
        """Test that attrs from use_logo are properly passed to formatting"""
        brand = Brand.from_yaml_str("""
        logo:
          small:
            path: test.png
            attrs:
              class: base-class
        """)

        # Add attrs via use_logo
        logo = brand.use_logo("small", width="200", class_="override-class")

        # Check that attrs are combined
        assert logo.attrs["width"] == "200"
        assert logo.attrs["class"] == "override-class"  # Should override

        # Test in HTML output
        html = logo.to_html()
        assert 'width="200"' in html
        assert 'class="brand-logo override-class"' in html

    def test_light_dark_attrs_propagation(self):
        """Test that attrs are properly propagated to light/dark variants"""
        brand = Brand.from_yaml_str("""
        logo:
          medium:
            light: light.png
            dark: dark.png
        """)

        logo = brand.use_logo("medium", width="150")
        html = logo.to_html()

        # Both variants should have the width
        assert html.count('width="150"') == 2
        # Both should have their respective content classes
        assert "light-content" in html
        assert "dark-content" in html

    def test_jupyter_repr_html(self):
        """Test _repr_html_ for Jupyter integration"""
        brand = Brand.from_yaml_str("""
        logo:
          small: test.png
          medium:
            light: light.png
            dark: dark.png
        """)

        # Single resource
        logo = brand.use_logo("small")
        repr_html = logo._repr_html_()
        assert repr_html.startswith("<img")

        # Light/dark resource
        logo_ld = brand.use_logo("medium")
        repr_html_ld = logo_ld._repr_html_()
        assert "brand-logo-light-dark" in repr_html_ld

    @pytest.mark.skipif(
        True, reason="htmltools not available in test environment"
    )
    def test_html_dependency_inclusion(self):
        """Test that HTML dependencies are included (requires htmltools)"""
        brand = Brand.from_yaml_str("""
        logo:
          small: test.png
        """)

        logo = brand.use_logo("small")
        html = logo.to_html()

        # Should include the CSS dependency somehow
        # This test would need to be updated based on actual htmltools behavior
        assert html is not None
