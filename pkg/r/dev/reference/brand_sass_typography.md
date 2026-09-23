# Generate Sass variables for brand typography

Creates Sass variables for typography settings with the
`brand_typography_` prefix. Font size values in pixels are converted to
rem units, and color references are resolved.

## Usage

``` r
brand_sass_typography(brand)
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
[`brand_sass_color()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_color.md),
[`brand_sass_color_palette()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_color_palette.md),
[`brand_sass_defaults_bootstrap()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_defaults_bootstrap.md),
[`brand_sass_fonts()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_fonts.md)

## Examples

``` r
brand <- list(
  typography = list(
    base = list(
      size = "16px",
      "line-height" = 1.5
    ),
    headings = list(
      weight = "bold",
      style = "normal"
    )
  )
)

brand_sass_typography(brand)
#> $defaults
#> $defaults$brand_typography_base_size
#> [1] "1rem !default"
#> 
#> $defaults$brand_typography_base_line_height
#> [1] "1.5 !default"
#> 
#> $defaults$brand_typography_headings_weight
#> [1] "bold !default"
#> 
#> $defaults$brand_typography_headings_style
#> [1] "normal !default"
#> 
#> 
```
