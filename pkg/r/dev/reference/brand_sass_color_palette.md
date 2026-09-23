# Generate Sass variables and CSS custom properties for brand color palette

Converts color palette entries from a brand object to Sass variables
with `brand-` prefix and CSS custom properties with `--brand-` prefix.

## Usage

``` r
brand_sass_color_palette(brand)
```

## Arguments

- brand:

  A list or string of YAML representing the brand, or a path to a
  brand.yml file.

## Value

A list with two components:

- `defaults`: Sass variable definitions with `!default` flag

- `rules`: CSS rules that define custom properties in `:root`

## See also

Other brand.yml Sass helpers:
[`brand_sass_color()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_color.md),
[`brand_sass_defaults_bootstrap()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_defaults_bootstrap.md),
[`brand_sass_fonts()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_fonts.md),
[`brand_sass_typography()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_typography.md)

## Examples

``` r
brand <- list(
  color = list(
    palette = list(
      primary = "#007bff",
      secondary = "#6c757d"
    )
  )
)

brand_sass_color_palette(brand)
#> $defaults
#> $defaults$`brand-primary`
#> [1] "#007bff !default"
#> 
#> $defaults$`brand-secondary`
#> [1] "#6c757d !default"
#> 
#> 
#> $rules
#> [1] ":root { --brand-primary:#007bff;--brand-secondary:#6c757d; }"
#> 
```
