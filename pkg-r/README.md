
# brand.yml

<!-- badges: start -->
[![CRAN status](https://www.r-pkg.org/badges/version/brand.yml)](https://CRAN.R-project.org/package=brand.yml)
[![R-CMD-check](https://github.com/posit-dev/brand-yml/actions/workflows/R-CMD-check.yaml/badge.svg)](https://github.com/posit-dev/brand-yml/actions/workflows/R-CMD-check.yaml)
<!-- badges: end -->

Centralize brand guidelines in a single 'brand.yml' file, enabling consistent theming across Quarto, Shiny, R applications, reports, and presentations with minimal configuration.


## Installation

You can install the development version of brand.yml from [GitHub](https://github.com/) with:

``` r
# install.packages("pak")
pak::pak("posit-dev/brand-yml/pkg-r")
```

## Example

Use `read_brand_yml()` to read in a brand.yml file into a validated and consistent R list.
You can provide a path to a local file, or `read_brand_yml()` will look for a `_brand.yml` file in your project.

``` r
library(brand.yml)

brand <- read_brand_yml(
  system.file("examples", "brand-posit.yml", package = "brand.yml")
)

brand$color |> str()
#> List of 12
#>  $ palette   :List of 7
#>   ..$ blue    : chr "#447099"
#>   ..$ orange  : chr "#EE6331"
#>   ..$ gray    : chr "#404041"
#>   ..$ white   : chr "#FFFFFF"
#>   ..$ teal    : chr "#419599"
#>   ..$ green   : chr "#72994E"
#>   ..$ burgundy: chr "#9A4665"
#>  $ foreground: chr "#151515"
#>  $ background: chr "#FFFFFF"
#>  $ primary   : chr "#447099"
#>  $ secondary : chr "#707073"
#>  $ tertiary  : chr "#C2C2C4"
#>  $ success   : chr "#72994E"
#>  $ info      : chr "#419599"
#>  $ warning   : chr "#EE6331"
#>  $ danger    : chr "#9A4665"
#>  $ light     : chr "#FFFFFF"
#>  $ dark      : chr "#404041"
```
