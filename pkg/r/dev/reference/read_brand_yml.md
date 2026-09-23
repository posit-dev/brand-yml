# Create a Brand instance from a Brand YAML file.

Reads a Brand YAML file or finds and reads a `_brand.yml` file and
returns a validated `Brand` instance.

## Usage

``` r
read_brand_yml(path = NULL)
```

## Arguments

- path:

  The path to the brand.yml file or a directory where `_brand.yml` is
  expected to be found.

## Value

A normalized `brand_yml` list from the brand.yml file.

## Details

By default, `read_brand_yml()` finds a project-specific `_brand.yml`
file, by looking in the current working directory directory or any
parent directory for a `_brand.yml`, `brand/_brand.yml` or
`_brand/_brand.yml` file (or the same variants with a `.yaml`
extension). When `path` is provided, `read_brand_yml()` looks for these
files in the provided directory; for automatic discovery,
`read_brand_yml()` starts the search in the working directory and moves
upward to find the `_brand.yml` file.

## References

<https://posit-dev.github.io/brand-yml/>

## Examples

``` r

# For this example: copy a brand.yml to a temporary directory
tmp_dir <- tempfile()
dir.create(tmp_dir)
file.copy(
  system.file("examples/brand-posit.yml", package = "brand.yml"),
  file.path(tmp_dir, "_brand.yml")
)
#> [1] TRUE

brand <- read_brand_yml(tmp_dir)
```
