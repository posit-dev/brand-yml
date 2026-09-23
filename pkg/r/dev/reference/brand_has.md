# Check if a brand has a specific nested element

Checks if a given `brand` object has a specific nested element
accessible via the additional arguments provided as key paths.

## Usage

``` r
brand_has(brand, ...)
```

## Arguments

- brand:

  A brand object created by
  [`read_brand_yml()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/read_brand_yml.md)
  or
  [`as_brand_yml()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/as_brand_yml.md).

- ...:

  One or more character strings or symbols representing the path to the
  nested element.

## Value

`TRUE` if the nested element exists in the brand object, `FALSE`
otherwise.

## See also

Other brand.yml helpers:
[`brand_color_pluck()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_color_pluck.md),
[`brand_pluck()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_pluck.md),
[`with_brand_yml_path()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/with_brand_yml_path.md)

## Examples

``` r
brand <- as_brand_yml(list(
  meta = list(name = "Example Brand"),
  color = list(primary = "#FF5733")
))

# Check if brand has a primary color
brand_has(brand, "color", "primary") # TRUE
#> [1] TRUE

# Check if brand has a secondary color
brand_has(brand, "color", "secondary") # FALSE
#> [1] FALSE
```
