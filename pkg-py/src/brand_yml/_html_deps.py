"""HTML dependencies for brand-yml"""

from __future__ import annotations

import htmltools

from .__version import __version_tuple__


def html_dep_brand_light_dark():
    """
    Generate HTML dependency for brand light/dark CSS.

    Returns
    -------
    :
        htmltools.HTMLDependency for brand light/dark styles
    """

    # TODO: Check if we're in a Quarto environment where CSS is handled differently
    # This would require detecting Quarto context, which isn't straightforward in Python
    # For now, always return the dependency
    # if in_quarto_environment():
    #     return None

    return htmltools.HTMLDependency(
        name="brand-logo-light-dark",
        version=".".join(map(str, __version_tuple__[:4])),
        source={"subdir": "www/shiny"},
        stylesheet={"href": "brand-light-dark.css"},
        all_files=False,
    )
