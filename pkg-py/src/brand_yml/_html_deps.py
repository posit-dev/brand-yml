"""HTML dependencies for brand-yml"""

from __future__ import annotations

try:
    import htmltools
except ImportError:
    htmltools = None


def html_dep_brand_light_dark():
    """
    Generate HTML dependency for brand light/dark CSS.

    Returns
    -------
    :
        htmltools.HTMLDependency for brand light/dark styles, or None if
        in a Quarto environment or htmltools is not available.
    """
    if htmltools is None:
        raise ImportError(
            "htmltools is required for HTML dependencies. Install with: pip install htmltools"
        )

    # TODO: Check if we're in a Quarto environment where CSS is handled differently
    # This would require detecting Quarto context, which isn't straightforward in Python
    # For now, always return the dependency
    # if in_quarto_environment():
    #     return None

    return htmltools.HTMLDependency(
        name="brand-logo-light-dark",
        version="0.1.0",  # TODO: Get from package version
        source={"subdir": "www/shiny"},
        stylesheet={"href": "brand-light-dark.css"},
        all_files=False,
    )
