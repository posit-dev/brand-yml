# Generate Sass variables for brand colors

Creates Sass variables for brand colors with the `brand_color_` prefix.
Excludes the color palette which is handled by
[`brand_sass_color_palette()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_color_palette.md).

## Usage

``` r
brand_sass_color(brand)
```

## Arguments

- brand:

  A list or string of YAML representing the brand, or a path to a
  brand.yml file.

## Value

A list with one component:

- `defaults`: Sass variable definitions with `!default` flag

## See also

Other brand.yml Sass helpers:
[`brand_sass_color_palette()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_color_palette.md),
[`brand_sass_defaults_bootstrap()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_defaults_bootstrap.md),
[`brand_sass_fonts()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_fonts.md),
[`brand_sass_typography()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_typography.md)

## Examples

``` r
brand <- list(
  color = list(
    primary = "#007bff",
    danger = "#dc3545"
  )
)

brand_sass_color(brand)
#> $defaults
#> $defaults$brand_color_primary
#> [1] "#007bff !default"
#> 
#> $defaults$brand_color_danger
#> [1] "#dc3545 !default"
#> 
#> 
```
