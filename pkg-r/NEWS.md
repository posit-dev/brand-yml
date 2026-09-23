# brand.yml (development version)

* Added support for the `color.link` theme color, used for hyperlinks. Like
  other theme colors, it accepts a scalar color, a reference to another color,
  or a `light`/`dark` mapping.

* `theme_brand_*()` no longer infers background and foreground colors from
  palette entries named `black` and `white`. Define `color.background` and
  `color.foreground`, or pass the colors explicitly to the theme helper.

# brand.yml 0.1.0

* Initial CRAN submission.
