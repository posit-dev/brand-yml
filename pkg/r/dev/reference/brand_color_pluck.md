# Extract a color value from a brand object

Safely extracts a color value from a `brand` object based on the
provided key. This function handles color references and resolves them,
including references to palette colors and other theme colors. It
detects and prevents cyclic references.

## Usage

``` r
brand_color_pluck(brand, key)
```

## Arguments

- brand:

  A brand object created by
  [`read_brand_yml()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/read_brand_yml.md)
  or
  [`as_brand_yml()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/as_brand_yml.md).

- key:

  A character string representing the color key to extract.

## Value

The resolved color value (typically a hex color code) if the key exists,
otherwise returns the key itself.

## Details

The function checks for the color key in both the main color theme and
the color palette. It can resolve references between colors (e.g., if
"primary" references "palette.blue"). If a cyclic reference is detected
(e.g., A references B which references A), the function will throw an
error.

## See also

Other brand.yml helpers:
[`brand_has()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_has.md),
[`brand_pluck()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_pluck.md),
[`with_brand_yml_path()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/with_brand_yml_path.md)

## Examples

``` r
brand <- as_brand_yml(list(
  color = list(
    primary = "blue",
    secondary = "info",
    info = "light-blue",
    palette = list(
      blue = "#004488",
      light_blue = "#c3ddff"
    )
  )
))

# Extract the primary color
brand_color_pluck(brand, "primary") # "#004488"
#> [1] "#004488"

# Extract a color that references another color
brand_color_pluck(brand, "info") # "#c3ddff"
#> [1] "light-blue"

# Extract a color that references another color
# which in turn references the palette
brand_color_pluck(brand, "secondary") # "#c3ddff"
#> [1] "light-blue"

# Extract a color that isn't defined
brand_color_pluck(brand, "green") # "green"
#> [1] "green"

# Use brand_pluck() if you need direct (resolved) values
brand_pluck(brand, "color", "primary") # "#004488"
#> [1] "#004488"
brand_pluck(brand, "color", "info") # "#c3ddff"
#> [1] "light-blue"
brand_pluck(brand, "color", "green") # NULL
#> NULL
```
