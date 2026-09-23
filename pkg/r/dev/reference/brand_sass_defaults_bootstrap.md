# Generate Sass variables and layer for Bootstrap defaults

Creates Sass variables and a sass layer from Bootstrap defaults defined
in the brand object. Allows overriding defaults from other sources like
Shiny themes.

## Usage

``` r
brand_sass_defaults_bootstrap(brand, overrides = "shiny.theme")
```

## Arguments

- brand:

  A list or string of YAML representing the brand, or a path to a
  brand.yml file.

- overrides:

  Path to override defaults, e.g., "shiny.theme"

## Value

A list with two components:

- `defaults`: Sass variable definitions with `!default` flag

- `layer`: A sass_layer object with functions, mixins, and rules

## See also

Other brand.yml Sass helpers:
[`brand_sass_color()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_color.md),
[`brand_sass_color_palette()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_color_palette.md),
[`brand_sass_fonts()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_fonts.md),
[`brand_sass_typography()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_typography.md)

## Examples

``` r
brand <- list(
  defaults = list(
    bootstrap = list(
      defaults = list(
        primary = "#007bff",
        enable_rounded = TRUE
      ),
      functions = "@function brand-function() { @return true; }"
    ),
    shiny = list(
      theme = list(
        defaults = list(
          primary = "#428bca"  # Override bootstrap primary
        )
      )
    )
  )
)

brand_sass_defaults_bootstrap(brand)
#> $defaults
#> $defaults$enable_rounded
#> [1] "true !default"
#> 
#> $defaults$primary
#> [1] "#428bca !default"
#> 
#> 
#> $layer
#> /* Sass Bundle */
#> @function brand-function() { @return true; }
#> /* *** */
#> 
```
