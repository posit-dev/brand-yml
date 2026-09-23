# Create a ggplot2 theme using brand colors

Create a ggplot2 theme using explicit colors or by automatically
extracting colors from a **brand.yml** file.

## Usage

``` r
theme_brand_ggplot2(
  brand = NULL,
  background = NULL,
  foreground = NULL,
  accent = NULL,
  ...,
  base_size = 11,
  title_size = base_size * 1.2,
  title_color = NULL,
  line_color = NULL,
  rect_fill = NULL,
  text_color = NULL,
  plot_background_fill = NULL,
  panel_background_fill = NULL,
  panel_grid_major_color = NULL,
  panel_grid_minor_color = NULL,
  axis_text_color = NULL,
  plot_caption_color = NULL
)
```

## Arguments

- brand:

  One of:

  - `NULL` (default): Automatically detect and read a \_brand.yml file

  - A path to a brand.yml file or directory containing \_brand.yml

  - A brand object (as returned by
    [`read_brand_yml()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/read_brand_yml.md)
    or
    [`as_brand_yml()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/as_brand_yml.md))

  - `FALSE`: Don't use a brand file; explicit colors must be provided

- background:

  The background color, defaults to `brand.color.background`. If
  provided directly, this value can be a valid R color or the name of a
  color in `brand.color` or `brand.color.palette`.

- foreground:

  The foreground color, defaults to `brand.color.foreground`. If
  provided directly, this value can be a valid R color or the name of a
  color in `brand.color` or `brand.color.palette`.

- accent:

  The accent color, defaults to `brand.color.primary` or
  `brand.color.palette.accent`. If provided directly, this value can be
  a valid R color or the name of a color in `brand.color` or
  `brand.color.palette`.

- ...:

  Reserved for future use.

- base_size:

  Base font size in points. Used for the `size` property of
  [`ggplot2::element_text()`](https://ggplot2.tidyverse.org/reference/element.html)
  in the `text` theme element.

- title_size:

  Title font size in points. Used for the `size` property of
  [`ggplot2::element_text()`](https://ggplot2.tidyverse.org/reference/element.html)
  in the `title` theme element. Defaults to `base_size * 1.2`.

- title_color, :

  Color for the `color` property of
  [`ggplot2::element_text()`](https://ggplot2.tidyverse.org/reference/element.html)
  in the `title` theme element. Can be a valid R color or the name of a
  color in `brand.color` or `brand.color.palette`. If not provided,
  defaults to the `foreground` color.

- line_color:

  Color for the `color` property of
  [`ggplot2::element_line()`](https://ggplot2.tidyverse.org/reference/element.html)
  in the `line` theme element. Can be a valid R color or the name of a
  color in `brand.color` or `brand.color.palette`. If not provided,
  defaults to a blend of foreground and background colors.

- rect_fill:

  Fill color for the `fill` property of
  [`ggplot2::element_rect()`](https://ggplot2.tidyverse.org/reference/element.html)
  in the `rect` theme element. Can be a valid R color or the name of a
  color in `brand.color` or `brand.color.palette`. If not provided,
  defaults to the background color.

- text_color:

  Color for the `color` property of
  [`ggplot2::element_text()`](https://ggplot2.tidyverse.org/reference/element.html)
  in the `text` theme element. Can be a valid R color or the name of a
  color in `brand.color` or `brand.color.palette`. If not provided,
  defaults to a blend of foreground and background colors.

- plot_background_fill:

  Fill color for the `fill` property of
  [`ggplot2::element_rect()`](https://ggplot2.tidyverse.org/reference/element.html)
  in the `plot.background` theme element. Can be a valid R color or the
  name of a color in `brand.color` or `brand.color.palette`. If not
  provided, defaults to the background color.

- panel_background_fill:

  Fill color for the `fill` property of
  [`ggplot2::element_rect()`](https://ggplot2.tidyverse.org/reference/element.html)
  in the `panel.background` theme element. Can be a valid R color or the
  name of a color in `brand.color` or `brand.color.palette`. If not
  provided, defaults to the background color.

- panel_grid_major_color:

  Color for the `color` property of
  [`ggplot2::element_line()`](https://ggplot2.tidyverse.org/reference/element.html)
  in the `panel.grid.major` theme element. Can be a valid R color or the
  name of a color in `brand.color` or `brand.color.palette`. If not
  provided, defaults to a blend of foreground and background colors.

- panel_grid_minor_color:

  Color for the `color` property of
  [`ggplot2::element_line()`](https://ggplot2.tidyverse.org/reference/element.html)
  in the `panel.grid.minor` theme element. Can be a valid R color or the
  name of a color in `brand.color` or `brand.color.palette`. If not
  provided, defaults to a blend of foreground and background colors.

- axis_text_color:

  Color for the `color` property of
  [`ggplot2::element_text()`](https://ggplot2.tidyverse.org/reference/element.html)
  in the `axis.text` theme element. Can be a valid R color or the name
  of a color in `brand.color` or `brand.color.palette`. If not provided,
  defaults to a blend of foreground and background colors.

- plot_caption_color:

  Color for the `color` property of
  [`ggplot2::element_text()`](https://ggplot2.tidyverse.org/reference/element.html)
  in the `plot.caption` theme element. Can be a valid R color or the
  name of a color in `brand.color` or `brand.color.palette`. If not
  provided, defaults to a blend of foreground and background colors.

## Value

A
[`ggplot2::theme()`](https://ggplot2.tidyverse.org/reference/theme.html)
object.

## Branded Theming

The `theme_brand_*` functions can be used in two ways:

1.  **With a brand.yml file**: The `theme_brand_*` functions use
    [`read_brand_yml()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/read_brand_yml.md)
    to automatically detect and use a `_brand.yml` file in your current
    project. You can also explicitly pass a path to a brand.yml file or
    a brand object (as returned by
    [`read_brand_yml()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/read_brand_yml.md)
    or created with
    [`as_brand_yml()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/as_brand_yml.md)).
    When a `brand` is provided, the theme functions will use the colors
    defined in the brand file automatically.

2.  **With explicit colors**: You can directly provide colors to
    override the default brand colors, or you can use `brand = FALSE` to
    ignore any project `_brand.yml` files and only use the explicitly
    provided colors.

## See also

Other branded theming functions:
[`theme_brand_flextable()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/theme_brand_flextable.md),
[`theme_brand_gt()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/theme_brand_gt.md),
[`theme_brand_plotly()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/theme_brand_plotly.md),
[`theme_brand_thematic()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/theme_brand_thematic.md)

## Examples

``` r
brand <- as_brand_yml('
color:
  palette:
    black: "#1A1A1A"
    white: "#F9F9F9"
    orange: "#FF6F20"
  foreground: black
  background: white
  primary: orange')

library(ggplot2)
ggplot(diamonds, aes(carat, price)) +
  geom_point() +
  theme_brand_ggplot2(brand)
```
