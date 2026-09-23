# Extract a nested element from a brand object

Safely extracts a nested element from a `brand` object using the
provided key path. Returns `NULL` if the element doesn't exist.

## Usage

``` r
brand_pluck(brand, ...)
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

The value of the nested element if it exists, `NULL` otherwise.

## See also

Other brand.yml helpers:
[`brand_color_pluck()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_color_pluck.md),
[`brand_has()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_has.md),
[`with_brand_yml_path()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/with_brand_yml_path.md)

## Examples

``` r
brand <- as_brand_yml(list(
  meta = list(name = "Example Brand"),
  color = list(primary = "#FF5733")
))

# Extract the primary color
brand_pluck(brand, "color", "primary") # "#FF5733"
#> [1] "#FF5733"

# Try to extract a non-existent element
brand_pluck(brand, "color", "secondary") # NULL
#> NULL
```
