# Generate Sass variables and CSS rules for brand fonts

Creates Sass variables and CSS rules for fonts defined in the brand
object. Supports Google fonts, Bunny fonts, and file-based fonts.

## Usage

``` r
brand_sass_fonts(brand)
```

## Arguments

- brand:

  A list or string of YAML representing the brand, or a path to a
  brand.yml file.

## Value

A list with two components:

- `defaults`: Sass variables for font definitions

- `rules`: CSS rules for applying fonts via classes

## See also

Other brand.yml Sass helpers:
[`brand_sass_color()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_color.md),
[`brand_sass_color_palette()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_color_palette.md),
[`brand_sass_defaults_bootstrap()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_defaults_bootstrap.md),
[`brand_sass_typography()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_sass_typography.md)

## Examples

``` r
brand <- list(
  typography = list(
    fonts = list(
      list(
        family = "Roboto",
        source = "google",
        weight = c(400, 700),
        style = "normal"
      )
    )
  )
)

brand_sass_fonts(brand)
#> $defaults
#> $defaults$`brand-font-roboto`
#> $families
#> [1] "Roboto"
#> 
#> $html_deps
#> function () 
#> dep_func(x)
#> <bytecode: 0x55e70c4ebf50>
#> <environment: 0x55e70c9a09f0>
#> attr(,"class")
#> [1] "shiny.tag.function"
#> 
#> $default_flag
#> [1] TRUE
#> 
#> attr(,"class")
#> [1] "font_collection" "list"           
#> 
#> 
#> $rules
#> $rules[[1]]
#> [1] ".brand-font-roboto { font-family: $brand-font-roboto; }"
#> 
#> 
```
