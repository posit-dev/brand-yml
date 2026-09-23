# Create a gt table theme using brand colors

Apply brand colors to a gt table.

## Usage

``` r
theme_brand_gt(table, brand = NULL, background = NULL, foreground = NULL)
```

## Arguments

- table:

  A gt table object to theme.

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

## Value

Returns a themed gt table object.

## See also

Other branded theming functions:
[`theme_brand_flextable()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/theme_brand_flextable.md),
[`theme_brand_ggplot2()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/theme_brand_ggplot2.md),
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

library(gt)
theme_brand_gt(
  gt(head(palmerpenguins::penguins)),
  brand
)


  

species
```
