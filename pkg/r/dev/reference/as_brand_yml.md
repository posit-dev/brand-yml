# Create a Brand instance from a list or character vector.

Create a Brand instance from a list or character vector.

## Usage

``` r
as_brand_yml(brand)
```

## Arguments

- brand:

  A list or string of YAML representing the brand, or a path to a
  brand.yml file.

## Value

A normalized `brand_yml` list.

## Examples

``` r
as_brand_yml("
meta:
  name: Example Brand

color:
  primary: '#FF5733'
  secondary: '#33FF57'
")
#> ## _brand.yml
#> meta:
#>   name:
#>     short: Example Brand
#>     full: Example Brand
#> color:
#>   primary: '#FF5733'
#>   secondary: '#33FF57'
#> 

as_brand_yml(list(
  meta = list(name = "Example Brand"),
  color = list(primary = "#FF5733", secondary = "#33FF57")
))
#> ## _brand.yml
#> meta:
#>   name:
#>     short: Example Brand
#>     full: Example Brand
#> color:
#>   primary: '#FF5733'
#>   secondary: '#33FF57'
#> 
```
