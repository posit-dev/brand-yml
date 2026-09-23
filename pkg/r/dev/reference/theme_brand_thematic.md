# Create a thematic theme using brand colors

Apply thematic styling using explicit colors or by automatically
extracting colors from a **brand.yml** file. This function sets global
theming for base R graphics.

## Usage

``` r
theme_brand_thematic(
  brand = NULL,
  background = NULL,
  foreground = NULL,
  accent = NULL,
  ...
)

theme_brand_thematic_on(
  brand = NULL,
  background = NULL,
  foreground = NULL,
  accent = NULL,
  ...
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

  Additional arguments passed to
  [`thematic::thematic_theme()`](https://rstudio.github.io/thematic/reference/thematic_on.html)
  or
  [`thematic::thematic_on()`](https://rstudio.github.io/thematic/reference/thematic_on.html).

## Value

[`thematic_theme()`](https://rstudio.github.io/thematic/reference/thematic_on.html)
returns a theme object as a list (which can be activated with
[`thematic_with_theme()`](https://rstudio.github.io/thematic/reference/thematic_with_theme.html)
or
[`thematic_set_theme()`](https://rstudio.github.io/thematic/reference/thematic_with_theme.html)).

[`thematic_on()`](https://rstudio.github.io/thematic/reference/thematic_on.html),
[`thematic_off()`](https://rstudio.github.io/thematic/reference/thematic_on.html),
and
[`thematic_shiny()`](https://rstudio.github.io/thematic/reference/thematic_on.html)
all return the previous global theme.

## Functions

- `theme_brand_thematic()`: brand.yml wrapper for
  [`thematic::thematic_theme()`](https://rstudio.github.io/thematic/reference/thematic_on.html)

- `theme_brand_thematic_on()`: brand.yml wrapper for
  [`thematic::thematic_theme()`](https://rstudio.github.io/thematic/reference/thematic_on.html)

## See also

See the "Branded Theming" section of
[`theme_brand_ggplot2()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/theme_brand_ggplot2.md)
for more details on how the `brand` argument works.

Other branded theming functions:
[`theme_brand_flextable()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/theme_brand_flextable.md),
[`theme_brand_ggplot2()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/theme_brand_ggplot2.md),
[`theme_brand_gt()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/theme_brand_gt.md),
[`theme_brand_plotly()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/theme_brand_plotly.md)

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

thematic::thematic_with_theme(theme_brand_thematic(brand), {
  ggplot(diamonds, aes(carat, price)) +
    geom_point()
})
```
